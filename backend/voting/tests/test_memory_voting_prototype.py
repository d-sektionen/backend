"""Integration checks for the experimental Redis-buffered voting path."""

from concurrent.futures import ThreadPoolExecutor
from datetime import date
from threading import Barrier
from unittest.mock import patch

from django.contrib.auth.models import User
from django.db import connections
from django.test import TransactionTestCase, override_settings
from rest_framework.test import APIRequestFactory, force_authenticate

from backend.membership.models import Member
from backend.voting import memory_buffer
from backend.voting.models import Alternative, Attendant, MadeVote, Meeting, Vote
from backend.voting.serializers import VoteDetailsSerializer, VoteListSerializer
from backend.voting.views import MadeVoteViewSet, VoteAdminViewSet


@override_settings(VOTING_BUFFER_REDIS_URL="redis://redis:6379/15")
class MemoryVotingTests(TransactionTestCase):
    def setUp(self):
        memory_buffer.client.cache_clear()
        publication = patch("backend.voting.signals.emit_event")
        publication.start()
        self.addCleanup(publication.stop)
        self.user = User.objects.create_user(username="voter01")
        self.admin = User.objects.create_superuser(username="buffer-admin", email="a@example.com", password="x")
        Member.objects.create(liu_id=self.user.username, membership_type="S")
        self.meeting = Meeting.objects.create(name="Buffered", clear_data=date(2026, 1, 1))
        Attendant.objects.create(meeting=self.meeting, user=self.user)
        self.vote = Vote.objects.create(meeting=self.meeting, question="Choose")
        self.alternative = Alternative.objects.create(vote=self.vote, text="Yes")
        memory_buffer.initialize(self.vote.pk)
        self.addCleanup(memory_buffer.call, "delete", memory_buffer.key(self.vote.pk))
        self.addCleanup(memory_buffer.client.cache_clear)

    def submit(self):
        request = APIRequestFactory().post(
            "/voting/made_votes/",
            {"vote_id": self.vote.pk, "alternative_id": self.alternative.pk},
            format="json",
        )
        force_authenticate(request, user=self.user)
        return MadeVoteViewSet.as_view({"post": "create"})(request)

    def close(self):
        request = APIRequestFactory().patch("/", {"open": False}, format="json")
        force_authenticate(request, user=self.admin)
        return VoteAdminViewSet.as_view({"patch": "partial_update"})(request, pk=self.vote.pk)

    def test_votes_remain_buffered_until_close(self):
        self.assertEqual(self.submit().status_code, 200)
        self.assertEqual(self.submit().status_code, 403)
        self.assertFalse(MadeVote.objects.filter(vote=self.vote).exists())
        self.alternative.refresh_from_db()
        self.assertEqual(self.alternative.num_votes, 0)
        self.assertTrue(memory_buffer.has_voted(self.vote.pk, self.user.pk))
        self.assertEqual(memory_buffer.snapshot(self.vote.pk)[1][self.alternative.pk], 1)
        request = APIRequestFactory().get("/")
        request.user = self.user
        self.assertTrue(VoteListSerializer(self.vote, context={"request": request}).data["has_voted"])
        self.assertEqual(VoteDetailsSerializer(self.vote).data["alternatives"][0]["num_votes"], 1)

        self.assertEqual(self.close().status_code, 200)
        self.vote.refresh_from_db()
        self.alternative.refresh_from_db()
        self.assertFalse(self.vote.open)
        self.assertEqual(MadeVote.objects.filter(vote=self.vote).count(), 1)
        self.assertEqual(self.alternative.num_votes, 1)
        self.assertFalse(memory_buffer.call("exists", memory_buffer.key(self.vote.pk)))
        self.assertEqual(self.close().status_code, 200)
        self.alternative.refresh_from_db()
        self.assertEqual(self.alternative.num_votes, 1)

    def test_frontend_can_close_with_full_put(self):
        self.assertEqual(self.submit().status_code, 200)
        request = APIRequestFactory().put(
            f"/voting/admin-votes/{self.vote.pk}/",
            {
                "question": self.vote.question,
                "open": False,
                "alternatives": [{"id": self.alternative.pk, "text": "Yes", "key": 1}],
                "meeting": self.meeting.pk,
            },
            format="json",
        )
        force_authenticate(request, user=self.admin)
        response = VoteAdminViewSet.as_view({"put": "update"})(request, pk=self.vote.pk)
        self.assertEqual(response.status_code, 200)
        self.vote.refresh_from_db()
        self.alternative.refresh_from_db()
        self.assertFalse(self.vote.open)
        self.assertEqual(self.alternative.num_votes, 1)

    def test_close_rejects_changes_to_ballot(self):
        request = APIRequestFactory().put(
            "/",
            {
                "question": "Changed",
                "open": False,
                "alternatives": [{"id": self.alternative.pk, "text": "Yes"}],
                "meeting": self.meeting.pk,
            },
            format="json",
        )
        force_authenticate(request, user=self.admin)
        response = VoteAdminViewSet.as_view({"put": "update"})(request, pk=self.vote.pk)
        self.assertEqual(response.status_code, 400)
        self.vote.refresh_from_db()
        self.assertTrue(self.vote.open)

    def test_failed_close_retains_buffer_for_retry(self):
        self.assertEqual(self.submit().status_code, 200)
        with (
            patch("backend.voting.views.MadeVote.objects.bulk_create", side_effect=RuntimeError("failed")),
            self.assertRaises(RuntimeError),
        ):
            self.close()
        self.vote.refresh_from_db()
        self.assertTrue(self.vote.open)
        self.assertFalse(MadeVote.objects.filter(vote=self.vote).exists())
        self.assertTrue(memory_buffer.has_voted(self.vote.pk, self.user.pk))
        self.assertEqual(self.submit().status_code, 503)
        self.assertEqual(self.close().status_code, 200)

    def test_admin_creation_initializes_shared_buffer(self):
        meeting = Meeting.objects.create(name="New meeting", clear_data=date(2026, 1, 1))
        request = APIRequestFactory().post(
            "/voting/admin-votes/",
            {"meeting": meeting.pk, "question": "New", "alternatives": [{"text": "Yes"}]},
            format="json",
        )
        force_authenticate(request, user=self.admin)
        response = VoteAdminViewSet.as_view({"post": "create"})(request)
        self.assertEqual(response.status_code, 201)
        vote_id = response.data["id"]
        self.addCleanup(memory_buffer.call, "delete", memory_buffer.key(vote_id))
        self.assertEqual(memory_buffer.snapshot(vote_id), ([], {}))

    def test_lost_buffer_requires_revote(self):
        self.assertEqual(self.submit().status_code, 200)
        memory_buffer.call("delete", memory_buffer.key(self.vote.pk))
        self.assertEqual(self.submit().status_code, 503)
        self.assertEqual(self.close().status_code, 503)
        self.assertFalse(MadeVote.objects.filter(vote=self.vote).exists())

    def test_parallel_duplicates_claim_once(self):
        with ThreadPoolExecutor(max_workers=8) as pool:
            accepted = list(pool.map(lambda _: memory_buffer.cast(self.vote.pk, self.user.pk, self.alternative.pk), range(20)))
        self.assertEqual(sum(accepted), 1)
        self.assertEqual(memory_buffer.snapshot(self.vote.pk)[1][self.alternative.pk], 1)

    def test_close_racing_with_vote_persists_every_accepted_vote(self):
        barrier = Barrier(2)

        def execute(operation):
            try:
                barrier.wait(timeout=5)
                return operation().status_code
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=2) as pool:
            vote = pool.submit(execute, self.submit)
            close = pool.submit(execute, self.close)
            vote_status, close_status = vote.result(), close.result()
        self.assertIn(vote_status, (200, 403))
        self.assertEqual(close_status, 200)
        self.alternative.refresh_from_db()
        self.assertEqual(self.alternative.num_votes, int(vote_status == 200))
        self.assertEqual(MadeVote.objects.filter(vote=self.vote).count(), int(vote_status == 200))
