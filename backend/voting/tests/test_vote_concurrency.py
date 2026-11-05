"""Exercise committed transactions on independent PostgreSQL connections."""

from concurrent.futures import ThreadPoolExecutor
from datetime import date
from threading import Barrier
from unittest import skipUnless
from unittest.mock import patch

from django.contrib.auth.models import User
from django.db import connection, connections
from django.test import TransactionTestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from backend.membership.models import Member
from backend.voting.casting import claim_vote, lock_choice
from backend.voting.models import (
    Alternative,
    Attendant,
    Ballot,
    MadeVote,
    Meeting,
    Vote,
)
from backend.voting.views import MadeVoteViewSet


@skipUnless(connection.vendor == "postgresql", "Requires PostgreSQL row locking")
class VoteConcurrencyTests(TransactionTestCase):
    def setUp(self):
        publication = patch("backend.voting.signals.emit_event")
        self.publication = publication.start()
        self.addCleanup(publication.stop)
        self.user = User.objects.create_user(username="race0001")
        Member.objects.create(liu_id=self.user.username, membership_type="S")
        self.meeting = Meeting.objects.create(name="Race", clear_data=date.today())
        self.vote = Vote.objects.create(meeting=self.meeting, question="Choose")
        Attendant.objects.create(meeting=self.meeting, user=self.user)
        self.alternatives = [
            Alternative.objects.create(vote=self.vote, text=str(i)) for i in range(2)
        ]

    def submit(self, alternative_id):
        try:
            request = APIRequestFactory().post(
                "/voting/made_votes/",
                {"vote_id": self.vote.pk, "alternative_id": alternative_id},
                format="json",
            )
            force_authenticate(request, user=self.user)
            return MadeVoteViewSet.as_view({"post": "create"})(request).status_code
        finally:
            connections.close_all()

    def test_concurrent_duplicate_submissions_count_once(self):
        # Pin both callers before claiming participation, with different choices.
        # Both must reach this point concurrently (the ballot locks are shared).
        barrier = Barrier(2)

        def simultaneous_claim(user_id, vote_id):
            barrier.wait(timeout=10)
            return claim_vote(user_id, vote_id)

        with patch("backend.voting.views.claim_vote", simultaneous_claim):
            with ThreadPoolExecutor(max_workers=2) as pool:
                statuses = list(
                    pool.map(self.submit, [a.pk for a in self.alternatives])
                )
        self.assertEqual(sorted(statuses), [200, 403])
        self.assertEqual(MadeVote.objects.filter(vote=self.vote).count(), 1)
        self.assertEqual(Ballot.objects.filter(alternative__vote=self.vote).count(), 1)

    def test_publication_runs_after_commit_and_failure_does_not_reject_vote(self):
        observed = []

        def fail_publication(event, data, room, timeout):
            observed.append(
                (connection.in_atomic_block, MadeVote.objects.count(), data)
            )
            raise RuntimeError("Redis unavailable")

        self.publication.side_effect = fail_publication
        with self.assertLogs("backend.voting.signals", level="WARNING"):
            self.assertEqual(self.submit(self.alternatives[0].pk), 200)
        self.assertEqual(len(observed), 1)
        self.assertEqual(observed[0][:2], (False, 1))
        self.assertEqual(set(observed[0][2]), {"id", "text", "vote", "meeting"})
        self.assertEqual(self.submit(self.alternatives[1].pk), 403)
        self.assertEqual(MadeVote.objects.count(), 1)
        self.assertEqual(
            Ballot.objects.filter(alternative=self.alternatives[0]).count(), 1
        )

    def test_ballot_failure_rolls_back_receipt_without_publication(self):
        from django.db import DatabaseError

        self.publication.reset_mock()
        with patch.object(
            Ballot.objects, "create", side_effect=DatabaseError("failure")
        ):
            with self.assertRaises(DatabaseError):
                self.submit(self.alternatives[0].pk)
        self.assertFalse(MadeVote.objects.exists())
        self.assertFalse(Ballot.objects.exists())
        self.publication.assert_not_called()

    def test_deleted_alternative_rolls_back_receipt_without_publication(self):
        def lock_then_lose_choice(alternative_id):
            choice = lock_choice(alternative_id)
            # Alternatives are not locked by voters; an admin edit can remove
            # one between validation and the ballot insert. The deferred
            # foreign key then fails at commit.
            Alternative.objects.filter(pk=alternative_id).delete()
            return choice

        self.publication.reset_mock()
        with patch("backend.voting.views.lock_choice", lock_then_lose_choice):
            self.assertEqual(self.submit(self.alternatives[0].pk), 404)
        self.assertFalse(MadeVote.objects.exists())
        self.assertFalse(Ballot.objects.exists())
        self.assertTrue(Alternative.objects.filter(pk=self.alternatives[0].pk).exists())
        self.publication.assert_not_called()

    def test_revoked_voting_rights_reject_without_counting(self):
        Attendant.objects.filter(user=self.user).update(has_voting_rights=False)
        self.assertEqual(self.submit(self.alternatives[0].pk), 403)
        self.assertFalse(MadeVote.objects.exists())

    def test_meeting_without_current_ballot_rejects_without_counting(self):
        Meeting.objects.filter(pk=self.meeting.pk).update(current_vote=None)
        self.assertEqual(self.submit(self.alternatives[0].pk), 403)
        self.assertFalse(MadeVote.objects.exists())

    def assert_revocation_precedes_vote(self, revoke):
        import time
        from django.db import transaction

        # A revocation owns the row before the vote reads it. Voting must wait
        # and validate the committed state, rather than read the old MVCC row.
        with ThreadPoolExecutor(max_workers=1) as pool:
            with transaction.atomic():
                revoke()
                future = pool.submit(self.submit, self.alternatives[0].pk)
                blocked = False
                deadline = time.monotonic() + 5
                while not future.done() and time.monotonic() < deadline:
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT pg_stat_clear_snapshot()")
                        cursor.execute(
                            "SELECT EXISTS (SELECT 1 FROM pg_stat_activity "
                            "WHERE datname=current_database() AND pid<>pg_backend_pid() "
                            "AND wait_event_type='Lock')"
                        )
                        blocked = cursor.fetchone()[0]
                    if blocked:
                        break
                    time.sleep(0.01)
            status = future.result(timeout=10)
        self.assertTrue(blocked, "Vote did not synchronize with in-flight revocation")
        self.assertEqual(status, 403)
        self.assertFalse(MadeVote.objects.exists())
        self.assertEqual(
            Ballot.objects.filter(alternative=self.alternatives[0]).count(), 0
        )

    def test_concurrent_ballot_closure(self):
        self.assert_revocation_precedes_vote(
            lambda: Vote.objects.filter(pk=self.vote.pk).update(open=False)
        )

    def test_concurrent_current_ballot_change(self):
        self.assert_revocation_precedes_vote(
            lambda: Meeting.objects.filter(pk=self.meeting.pk).update(current_vote=None)
        )

    def test_concurrent_attendance_revocation(self):
        self.assert_revocation_precedes_vote(
            lambda: Attendant.objects.filter(user=self.user).delete()
        )

    def test_concurrent_voting_rights_revocation(self):
        self.assert_revocation_precedes_vote(
            lambda: Attendant.objects.filter(user=self.user).update(
                has_voting_rights=False
            )
        )

    def test_concurrent_membership_revocation(self):
        self.assert_revocation_precedes_vote(
            lambda: Member.objects.filter(liu_id=self.user.username).update(
                membership_type="A"
            )
        )

    def test_voter_holds_validation_locks_until_commit(self):
        import time
        from threading import Event

        ready, release = Event(), Event()

        def pause_after_receipt(user_id, vote_id):
            result = claim_vote(user_id, vote_id)
            ready.set()
            if not release.wait(10):
                raise TimeoutError("Test did not release vote")
            return result

        def close_ballot():
            try:
                Vote.objects.filter(pk=self.vote.pk).update(open=False)
            finally:
                connections.close_all()

        with patch("backend.voting.views.claim_vote", pause_after_receipt):
            with ThreadPoolExecutor(max_workers=2) as pool:
                cast = pool.submit(self.submit, self.alternatives[0].pk)
                try:
                    self.assertTrue(ready.wait(5))
                    close = pool.submit(close_ballot)
                    blocked = False
                    deadline = time.monotonic() + 5
                    while not close.done() and time.monotonic() < deadline:
                        with connection.cursor() as cursor:
                            cursor.execute(
                                "SELECT EXISTS (SELECT 1 FROM pg_stat_activity "
                                "WHERE datname=current_database() AND pid<>pg_backend_pid() "
                                "AND wait_event_type='Lock')"
                            )
                            blocked = cursor.fetchone()[0]
                        if blocked:
                            break
                        time.sleep(0.01)
                finally:
                    release.set()
                self.assertEqual(cast.result(timeout=10), 200)
                close.result(timeout=10)
        self.assertTrue(blocked, "Closure overtook a validated vote")
        self.assertEqual(self.submit(self.alternatives[1].pk), 403)
        self.assertEqual(MadeVote.objects.count(), 1)

    def test_connection_loss_rolls_back_both_and_allows_recast(self):
        from threading import Event
        from django.db import OperationalError
        from rest_framework.test import APIClient

        ready, release = Event(), Event()
        backend_pid = []

        def lose_connection_after_receipt(user_id, vote_id):
            result = claim_vote(user_id, vote_id)
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_backend_pid()")
                backend_pid.append(cursor.fetchone()[0])
            ready.set()
            if not release.wait(10):
                raise TimeoutError("Test did not release vote")
            return result

        with patch("backend.voting.views.claim_vote", lose_connection_after_receipt):
            with ThreadPoolExecutor(max_workers=1) as pool:
                cast = pool.submit(self.submit, self.alternatives[0].pk)
                try:
                    self.assertTrue(ready.wait(5))
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT pg_terminate_backend(%s)", backend_pid)
                        self.assertTrue(cursor.fetchone()[0])
                finally:
                    release.set()
                with self.assertRaises(OperationalError):
                    cast.result(timeout=10)
        self.assertFalse(MadeVote.objects.exists())
        self.assertEqual(
            Ballot.objects.filter(alternative=self.alternatives[0]).count(), 0
        )

        client = APIClient()
        client.force_authenticate(self.user)
        url = f"/voting/votes/?meeting_id={self.meeting.pk}"
        self.assertFalse(client.get(url).data[0]["has_voted"])
        self.assertEqual(self.submit(self.alternatives[1].pk), 200)
        self.assertTrue(client.get(url).data[0]["has_voted"])
        self.assertEqual(self.submit(self.alternatives[0].pk), 403)
        self.assertEqual(
            Ballot.objects.filter(alternative=self.alternatives[1]).count(), 1
        )
