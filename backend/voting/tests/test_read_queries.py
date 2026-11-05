"""Meeting polling should keep its database work bounded as lists grow."""

from datetime import date
from unittest.mock import patch

from django.db import connection
from django.test.utils import CaptureQueriesContext

from backend.account.tests.utils import AuthenticatedTestCase
from backend.voting.models import Alternative, Attendant, MadeVote, Meeting, Vote


class VotingReadTests(AuthenticatedTestCase):
    @classmethod
    def setUpTestData(cls):
        with patch("backend.voting.signals.emit_event"):
            cls.meeting = Meeting.objects.create(name="Reads", clear_data=date.today())
            cls.vote = Vote.objects.create(meeting=cls.meeting, question="Current")
            cls.alternative = Alternative.objects.create(
                vote=cls.vote, text="Yes", num_votes=1
            )
            Attendant.objects.create(user=cls.member, meeting=cls.meeting)
            MadeVote.objects.create(user=cls.member, vote=cls.vote)

    def admin_ballots(self):
        with CaptureQueriesContext(connection) as queries:
            response = self.admin_client.get("/voting/admin-votes/")
        self.assertEqual(response.status_code, 200)
        return len(queries), response.data

    def test_ballot_list_query_count_does_not_grow_with_history(self):
        # Warm the admin permission cache equally before both measurements.
        self.admin_ballots()
        before, _ = self.admin_ballots()
        history = Vote.objects.bulk_create(
            [Vote(meeting=self.meeting, question=str(i), open=False) for i in range(20)]
        )
        Alternative.objects.bulk_create(
            [Alternative(vote=vote, text="Old") for vote in history]
        )
        after, data = self.admin_ballots()
        self.assertEqual(len(data), 21)
        self.assertEqual(after, before)

    def test_participation_is_user_specific_and_public_choices_hide_counts(self):
        member = self.member_client.get(f"/voting/votes/?meeting_id={self.meeting.pk}")
        self.assertEqual(member.status_code, 200)
        self.assertTrue(member.data[0]["has_voted"])
        self.assertNotIn("num_votes", member.data[0]["alternatives"][0])
        _, admin = self.admin_ballots()
        self.assertFalse(admin[0]["has_voted"])
        result = self.admin_client.get(f"/voting/admin-votes/{self.vote.pk}/")
        self.assertEqual(result.data["alternatives"][0]["num_votes"], 1)
        denied = self.member_client.get(f"/voting/admin-votes/{self.vote.pk}/")
        self.assertEqual(denied.status_code, 403)

    def test_attendant_list_queries_do_not_grow_with_attendance(self):
        from backend.account.tests.factories import UserFactory

        url = f"/voting/attendants/?meeting_id={self.meeting.pk}"
        self.admin_client.get(url)
        with CaptureQueriesContext(connection) as before:
            response = self.admin_client.get(url)
        self.assertEqual(response.status_code, 200)
        users = UserFactory.create_batch(10)
        Attendant.objects.bulk_create(
            [Attendant(user=user, meeting=self.meeting) for user in users]
        )
        with CaptureQueriesContext(connection) as after:
            response = self.admin_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 11)
        self.assertEqual(len(after), len(before))
