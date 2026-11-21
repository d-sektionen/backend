from collections import Counter
from datetime import date
from unittest.mock import patch

from django.db import connection, transaction
from django.test import TransactionTestCase
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient

from backend.account.tests.factories import UserFactory
from backend.account.tests.utils import AuthenticatedTestCase
from backend.membership.tests.factories import MemberFactory
from backend.voting.models import (
    Alternative,
    Attendant,
    Ballot,
    MadeVote,
    Meeting,
    SpeakerRequest,
    Vote,
)


class EndpointQueryTests(AuthenticatedTestCase):
    @classmethod
    def setUpTestData(cls):
        with patch("backend.voting.signals.emit_event"):
            cls.meeting = Meeting.objects.create(
                name="Endpoint query checks",
                clear_data=date.today(),
                open_attendance=True,
            )
            Attendant.objects.create(user=cls.member, meeting=cls.meeting)
            cls.vote = Vote.objects.create(meeting=cls.meeting, question="Current")
            yes = Alternative.objects.create(vote=cls.vote, text="Yes")
            Ballot.objects.create(alternative=yes)
            MadeVote.objects.create(user=cls.member, vote=cls.vote)
            SpeakerRequest.objects.create(user=cls.member, meeting=cls.meeting)

    def measured_get(self, client, url):
        with CaptureQueriesContext(connection) as queries:
            response = client.get(url)
        self.assertEqual(response.status_code, 200)
        return len(queries), response.data

    def test_member_meeting_list_queries_stay_bounded_and_attendance_is_user_specific(
        self,
    ):
        before, _ = self.measured_get(self.member_client, "/voting/meetings/")
        for i in range(8):
            Meeting.objects.create(
                name=str(i), clear_data=date.today(), open_attendance=True
            )
        after, data = self.measured_get(self.member_client, "/voting/meetings/")
        self.assertEqual(after, before)
        self.assertEqual(len(data), 9)
        self.assertEqual([m["id"] for m in data if m["attending"]], [self.meeting.pk])
        hidden = Meeting.objects.create(
            name="Hidden", clear_data=date.today(), open_attendance=False
        )
        self.assertNotIn(
            hidden.pk,
            [m["id"] for m in self.member_client.get("/voting/meetings/").data],
        )
        Attendant.objects.create(user=self.member, meeting=hidden)
        self.assertIn(
            hidden.pk,
            [m["id"] for m in self.member_client.get("/voting/meetings/").data],
        )

    def test_guest_meeting_list_queries_stay_bounded_and_hide_uninvited_meetings(self):
        with patch("backend.voting.signals.emit_event"):
            Attendant.objects.create(
                user=self.non_member, meeting=self.meeting, has_voting_rights=False
            )
        before, _ = self.measured_get(self.non_member_client, "/voting/guest-meetings/")
        for i in range(8):
            meeting = Meeting.objects.create(name=str(i), clear_data=date.today())
            Attendant.objects.bulk_create(
                [
                    Attendant(
                        user=self.non_member, meeting=meeting, has_voting_rights=False
                    )
                ]
            )
        after, data = self.measured_get(
            self.non_member_client, "/voting/guest-meetings/"
        )
        self.assertEqual(after, before)
        self.assertEqual(len(data), 9)
        self.assertTrue(all(m["attending"] for m in data))

    def test_speaker_list_queries_stay_bounded_and_keep_order_and_user_fields(self):
        url = f"/voting/speakers/?meeting_id={self.meeting.pk}"
        before, _ = self.measured_get(self.member_client, url)
        users = UserFactory.create_batch(10)
        SpeakerRequest.objects.bulk_create(
            [
                SpeakerRequest(user=u, meeting=self.meeting, prioritized=i % 2 == 0)
                for i, u in enumerate(users)
            ]
        )
        after, data = self.measured_get(self.member_client, url)
        self.assertEqual(after, before)
        self.assertEqual(len(data), 11)
        self.assertTrue(all(s["prioritized"] for s in data[:5]))
        self.assertEqual(
            set(data[0]["user"]),
            {"id", "username", "first_name", "last_name", "pretty_name"},
        )

    def test_captured_admin_event_id_filters_only_list_and_keeps_unfiltered_history(
        self,
    ):
        with patch("backend.voting.signals.emit_event"):
            other = Meeting.objects.create(name="Other", clear_data=date.today())
            Vote.objects.create(meeting=other, question="Other", open=False)
        for parameter in ["event_id", "meeting_id"]:
            data = self.admin_client.get(
                f"/voting/admin-votes/?{parameter}={self.meeting.pk}"
            ).data
            self.assertEqual([v["id"] for v in data], [self.vote.pk])
        self.assertEqual(len(self.admin_client.get("/voting/admin-votes/").data), 2)
        self.assertEqual(
            self.admin_client.get("/voting/admin-votes/?event_id=bad").status_code, 400
        )
        self.assertEqual(
            self.admin_client.get(
                f"/voting/admin-votes/?event_id={other.pk}&meeting_id={self.meeting.pk}"
            ).data,
            [],
        )

        self.assertEqual(
            self.admin_client.get(
                f"/voting/admin-votes/{self.vote.pk}/?event_id={other.pk}"
            ).status_code,
            200,
        )
        self.assertEqual(
            self.member_client.get(
                f"/voting/admin-votes/?event_id={self.meeting.pk}"
            ).status_code,
            403,
        )

    def test_clear_members_is_bounded_keeps_guests_tallies_receipts_and_events(self):
        guest = UserFactory()
        MemberFactory(liu_id=guest.username, membership_type="A")
        with patch("backend.voting.signals.emit_event"):
            # Membership, not the possibly stale voting-right flag, determines
            # which attendees the existing clear action removes.
            Attendant.objects.create(
                user=guest, meeting=self.meeting, has_voting_rights=True
            )
        url = f"/voting/attendants/clear/?meeting_id={self.meeting.pk}"
        with (
            patch("backend.voting.signals.emit_event"),
            self.captureOnCommitCallbacks(execute=True),
        ):
            with CaptureQueriesContext(connection) as before:
                self.assertEqual(self.admin_client.delete(url).status_code, 204)
        users = UserFactory.create_batch(12)
        for user in users:
            MemberFactory(liu_id=user.username, membership_type="S")
        Attendant.objects.bulk_create(
            [
                Attendant(user=u, meeting=self.meeting, has_voting_rights=False)
                for u in users
            ]
        )
        with (
            patch("backend.voting.signals.emit_event") as emit,
            self.captureOnCommitCallbacks(execute=True),
        ):
            with CaptureQueriesContext(connection) as after:
                self.assertEqual(self.admin_client.delete(url).status_code, 204)
        self.assertEqual(
            sum(q["sql"].startswith("SELECT") for q in after),
            sum(q["sql"].startswith("SELECT") for q in before),
        )
        self.assertEqual(Counter(q["sql"].split()[0] for q in after)["DELETE"], 1)
        self.assertEqual(Attendant.objects.get(meeting=self.meeting).user, guest)
        self.assertEqual(emit.call_count, 12)
        self.assertTrue(
            all(c.args[0] == "delete_attendant" for c in emit.call_args_list)
        )
        self.assertEqual(MadeVote.objects.filter(vote=self.vote).count(), 1)
        self.assertEqual(Ballot.objects.filter(alternative__vote=self.vote).count(), 1)

    def test_admin_attendee_creation_reuses_the_validated_user(self):
        guest = UserFactory()
        with (
            patch("backend.voting.signals.emit_event"),
            self.captureOnCommitCallbacks(execute=True),
        ):
            with CaptureQueriesContext(connection) as queries:
                response = self.admin_client.post(
                    "/voting/attendants/",
                    {
                        "user_username": guest.username,
                        "meeting_id": self.meeting.pk,
                        "has_voting_rights": False,
                    },
                    format="json",
                )
        self.assertEqual(response.status_code, 201)
        user_reads = [q for q in queries if 'FROM "auth_user"' in q["sql"]]
        self.assertEqual(len(user_reads), 1)
        self.assertEqual(response.data["user"]["id"], guest.pk)

    def test_duplicate_self_attendance_is_a_client_error_and_never_adds_row(self):
        with (
            transaction.atomic(),
            patch.object(self.member_client, "raise_request_exception", False),
        ):
            response = self.member_client.post(
                "/voting/attend/", {"meeting_id": self.meeting.pk}, format="json"
            )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            Attendant.objects.filter(user=self.member, meeting=self.meeting).count(), 1
        )


class AttendanceDeletionCommitTests(TransactionTestCase):
    def test_deletion_notifications_observe_committed_rows_and_survive_transport_failure(
        self,
    ):
        with patch("backend.voting.signals.emit_event"):
            admin = UserFactory(admin=True)
            member = UserFactory()
            MemberFactory(liu_id=member.username, membership_type="S")
            meeting = Meeting.objects.create(
                name="Commit check", clear_data=date.today()
            )
            Attendant.objects.create(user=member, meeting=meeting)
        client = APIClient()
        client.force_authenticate(admin)
        states = []

        def failed_transport(*args, **kwargs):
            states.append(
                (
                    connection.in_atomic_block,
                    Attendant.objects.filter(meeting=meeting).exists(),
                )
            )
            raise ConnectionError("Local publication test")

        with (
            patch("backend.voting.signals.emit_event", side_effect=failed_transport),
            self.assertLogs("backend.voting.signals", level="WARNING"),
        ):
            response = client.delete(
                f"/voting/attendants/clear/?meeting_id={meeting.pk}"
            )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(states, [(False, False)])

    def test_self_attendance_publication_observes_committed_row(self):
        with patch("backend.voting.signals.emit_event"):
            member = UserFactory()
            MemberFactory(liu_id=member.username, membership_type="S")
            meeting = Meeting.objects.create(
                name="Create commit", clear_data=date.today(), open_attendance=True
            )
        states = []

        def published(*args, **kwargs):
            states.append(
                (
                    connection.in_atomic_block,
                    Attendant.objects.filter(user=member, meeting=meeting).exists(),
                )
            )

        client = APIClient()
        client.force_authenticate(member)
        with patch("backend.voting.signals.emit_event", side_effect=published):
            response = client.post(
                "/voting/attend/", {"meeting_id": meeting.pk}, format="json"
            )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["meeting"]["attending"])
        self.assertEqual(states, [(False, True)])

    def test_rolled_back_bulk_deletion_publishes_nothing(self):
        with patch("backend.voting.signals.emit_event"):
            user = UserFactory()
            meeting = Meeting.objects.create(
                name="Rollback event", clear_data=date.today()
            )
            attendee = Attendant.objects.create(user=user, meeting=meeting)
        with patch("backend.voting.signals.emit_event") as emit:
            with transaction.atomic():
                Attendant.objects.filter(pk=attendee.pk).delete()
                transaction.set_rollback(True)
            emit.assert_not_called()
        self.assertTrue(Attendant.objects.filter(pk=attendee.pk).exists())

    def test_concurrent_self_attendance_retries_create_once(self):
        if connection.vendor != "postgresql":
            self.skipTest("PostgreSQL concurrency regression")
        import threading
        from concurrent.futures import ThreadPoolExecutor
        from django.db import connections

        with patch("backend.voting.signals.emit_event"):
            member = UserFactory()
            MemberFactory(liu_id=member.username, membership_type="S")
            meeting = Meeting.objects.create(
                name="Concurrent check-in",
                clear_data=date.today(),
                open_attendance=True,
            )
        start = threading.Barrier(2)

        def submit():
            try:
                client = APIClient()
                client.raise_request_exception = False
                client.force_authenticate(member)
                start.wait(timeout=3)
                return client.post(
                    "/voting/attend/", {"meeting_id": meeting.pk}, format="json"
                ).status_code
            finally:
                connections.close_all()

        with (
            patch("backend.voting.signals.emit_event") as emit,
            ThreadPoolExecutor(max_workers=2) as pool,
        ):
            results = list(pool.map(lambda _: submit(), range(2)))
        self.assertEqual(sorted(results), [201, 400])
        self.assertEqual(
            Attendant.objects.filter(user=member, meeting=meeting).count(), 1
        )
        self.assertEqual(emit.call_count, 1)


class AdminAlternativeConcurrencyTests(TransactionTestCase):
    def test_admin_full_put_does_not_overwrite_a_concurrent_vote_tally(self):
        if connection.vendor != "postgresql":
            self.skipTest("PostgreSQL concurrency regression")
        from concurrent.futures import ThreadPoolExecutor
        from django.db import connections
        from backend.voting.serializers import PublicAlternativeSerializer

        with patch("backend.voting.signals.emit_event"):
            admin = UserFactory(admin=True)
            voter = UserFactory()
            MemberFactory(liu_id=voter.username, membership_type="S")
            meeting = Meeting.objects.create(
                name="Concurrent admin edit", clear_data=date.today()
            )
            Attendant.objects.create(user=voter, meeting=meeting)
            vote = Vote.objects.create(meeting=meeting, question="Live ballot")
            yes = Alternative.objects.create(vote=vote, text="Yes")
            no = Alternative.objects.create(vote=vote, text="No")
        client = APIClient()
        client.force_authenticate(admin)
        original = PublicAlternativeSerializer.update
        injected = False

        def cast():
            try:
                voter_client = APIClient()
                voter_client.force_authenticate(voter)
                return voter_client.post(
                    "/voting/made_votes/",
                    {"vote_id": vote.pk, "alternative_id": yes.pk},
                    format="json",
                ).status_code
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=1) as pool:

            def update(serializer, instance, validated_data):
                nonlocal injected
                if instance.pk == yes.pk and not injected:
                    # WritableNested loaded the child's tally already. A real
                    # cast now commits before the metadata update saves it.
                    injected = True
                    self.assertEqual(pool.submit(cast).result(timeout=5), 200)
                return original(serializer, instance, validated_data)

            with (
                patch.object(PublicAlternativeSerializer, "update", update),
                patch("backend.voting.signals.emit_event"),
            ):
                response = client.put(
                    f"/voting/admin-votes/{vote.pk}/",
                    {
                        "meeting": meeting.pk,
                        "question": "Edited while open",
                        "open": True,
                        "alternatives": [
                            {"id": yes.pk, "text": "Edited Yes"},
                            {"id": no.pk, "text": "No"},
                        ],
                    },
                    format="json",
                )
        self.assertTrue(injected)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(MadeVote.objects.filter(vote=vote).count(), 1)
        self.assertEqual(Ballot.objects.filter(alternative=yes).count(), 1)
        self.assertEqual(Alternative.objects.get(pk=yes.pk).text, "Edited Yes")


class BulkPublicationFailureTests(TransactionTestCase):
    def test_clear_stops_retrying_publication_after_first_failure(self):
        with patch("backend.voting.signals.emit_event"):
            admin = UserFactory(admin=True)
            meeting = Meeting.objects.create(
                name="Failed bulk publication", clear_data=date.today()
            )
            members = UserFactory.create_batch(4)
            for member in members:
                MemberFactory(liu_id=member.username, membership_type="S")
            Attendant.objects.bulk_create(
                [Attendant(user=member, meeting=meeting) for member in members]
            )
        client = APIClient()
        client.force_authenticate(admin)
        with (
            patch(
                "backend.voting.signals.emit_event",
                side_effect=ConnectionError("Local test"),
            ) as emit,
            self.assertLogs("backend.voting.signals", level="WARNING"),
        ):
            response = client.delete(
                f"/voting/attendants/clear/?meeting_id={meeting.pk}"
            )
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Attendant.objects.filter(meeting=meeting).exists())
        self.assertEqual(emit.call_count, 1)
        # Failure state belongs to this operation, so later requests still emit.
        with patch("backend.voting.signals.emit_event") as emit:
            response = client.post(
                "/voting/attendants/",
                {
                    "user_username": members[0].username,
                    "meeting_id": meeting.pk,
                    "has_voting_rights": True,
                },
                format="json",
            )
        self.assertEqual(response.status_code, 201)
        emit.assert_called_once()


class BallotPointerConcurrencyTests(TransactionTestCase):
    def test_opening_a_ballot_does_not_restore_stale_meeting_metadata(self):
        if connection.vendor != "postgresql":
            self.skipTest("PostgreSQL concurrency regression")
        from concurrent.futures import ThreadPoolExecutor
        from django.db import connections

        with patch("backend.voting.signals.emit_event"):
            admin = UserFactory(admin=True)
            meeting = Meeting.objects.create(
                name="Old name", clear_data=date.today(), open_attendance=True
            )
        client = APIClient()
        client.force_authenticate(admin)
        original = Meeting.save
        injected = False

        def update_metadata():
            try:
                concurrent = APIClient()
                concurrent.force_authenticate(admin)
                return concurrent.patch(
                    f"/voting/admin-meetings/{meeting.pk}/",
                    {
                        "name": "Concurrent name",
                        "open_attendance": False,
                    },
                    format="json",
                ).status_code
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=1) as pool:

            def save(instance, *args, **kwargs):
                nonlocal injected
                if (
                    instance.pk == meeting.pk
                    and instance.current_vote_id is not None
                    and not injected
                ):
                    injected = True
                    self.assertEqual(
                        pool.submit(update_metadata).result(timeout=5), 200
                    )
                return original(instance, *args, **kwargs)

            with (
                patch.object(Meeting, "save", save),
                patch("backend.voting.signals.emit_event"),
            ):
                response = client.post(
                    "/voting/admin-votes/",
                    {
                        "meeting": meeting.pk,
                        "question": "New",
                        "open": True,
                        "alternatives": [{"text": "Yes"}, {"text": "No"}],
                    },
                    format="json",
                )
        self.assertTrue(injected)
        self.assertEqual(response.status_code, 201)
        meeting.refresh_from_db()
        self.assertEqual(meeting.name, "Concurrent name")
        self.assertFalse(meeting.open_attendance)
        self.assertEqual(meeting.current_vote_id, response.data["id"])
