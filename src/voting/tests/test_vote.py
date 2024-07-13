import json

from account.tests.utils import AuthenticatedTestCase
from voting.models import Vote
from voting.tests.factories import (
    AlternativeFactory,
    AttendantFactory,
    MeetingFactory,
    VoteFactory,
)

NB_OF_ATTENDANTS = 10


class VoteTest(AuthenticatedTestCase):
    """Tests for endpoints under /voting/votes and /voting/admin-votes/."""
    @classmethod
    def setUpTestData(cls):
        cls.meeting = MeetingFactory.create(open_attendance=True)
        cls.hidden_meeting = MeetingFactory.create(open_attendance=False)
        cls.meeting_with_votes = MeetingFactory.create(open_attendance=True)
        cls.alternatives = AlternativeFactory.create_batch(
            4, vote=cls.meeting_with_votes.current_vote
        )

        VoteFactory.create(meeting=cls.meeting_with_votes, open=False)
        # Make member an attendant of meeting_with_votes for these tests
        AttendantFactory.create(meeting=cls.meeting_with_votes, user=cls.member)

    def test_list_current_vote_for_specific_meeting_as_member(self):
        response = self.member_client.get(
            f"/voting/votes/?meeting_id={self.meeting_with_votes.id}"
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode("utf-8"))

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["meeting"], self.meeting_with_votes.id)
        self.assertEqual(len(data[0]["alternatives"]), 4)

    def test_list_all_votes_as_admin(self):
        response = self.admin_client.get("/voting/admin-votes/")

        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(response_data), 4)
        [self.assertTrue("question" in vote) for vote in response_data]

    def test_list_specific_vote_as_member(self):
        response = self.member_client.get(
            f"/voting/admin-votes/{self.meeting_with_votes.current_vote.id}/"
        )

        self.assertEqual(response.status_code, 403)

    def test_list_specific_vote_as_admin(self):
        response = self.admin_client.get(
            f"/voting/admin-votes/{self.meeting_with_votes.current_vote.id}/"
        )

        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content.decode("utf-8"))
        self.assertTrue("question" in response_data)
        self.assertEqual(response_data["id"], self.meeting_with_votes.current_vote.id)
        self.assertEqual(len(response_data["alternatives"]), 4)

    def test_create_vote_as_member(self):
        meeting = MeetingFactory.create()
        vote_to_create = VoteFactory.build(meeting=meeting)
        alternatives = AlternativeFactory.build(vote=vote_to_create)
        data = {
            "question": vote_to_create.question,
            "open": vote_to_create.open,
            "alternatives": [{"id": alternatives.id, "text": alternatives.id}],
            "meeting": meeting.id,
        }
        response = self.member_client.post(
            "/voting/admin-votes/",
            data=data,
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_create_vote_as_admin(self):
        meeting = MeetingFactory.create()
        vote_to_create = VoteFactory.build(meeting=meeting)
        alternatives = AlternativeFactory.build(vote=vote_to_create)

        data = {
            "question": vote_to_create.question,
            "open": vote_to_create.open,
            "alternatives": [{"text": alternatives.text}],
            "meeting": meeting.id,
        }
        response = self.admin_client.post(
            "/voting/admin-votes/",
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, 201)

        response_data = json.loads(response.content.decode("utf-8"))
        db_vote = Vote.objects.filter(id=response_data["id"]).first()

        self.assertEqual(db_vote.question, vote_to_create.question)

    def test_create_vote_with_no_alternatives(self):
        vote_to_create = VoteFactory.build(meeting=self.meeting, open=False)

        data = {
            "question": vote_to_create.question,
            "open": vote_to_create.open,
            # This should be non-destructive so we can use meeting stored on the class
            "meeting": self.meeting.id,
        }
        response = self.admin_client.post(
            "/voting/admin-votes/",
            data=data,
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_delete_vote_as_member(self):
        response = self.admin_client.delete("/voting/admin-votes/")
        self.assertEqual(response.status_code, 405)

    def test_patch_update_vote_as_member(self):
        vote_to_create = VoteFactory.build(meeting=self.meeting)

        data = {
            "question": vote_to_create.question,
            "open": vote_to_create.open,
            "alternatives": [],
            "meeting": self.meeting.id,
        }
        response = self.member_client.patch(
            f"/voting/admin-votes/{self.meeting.current_vote.id}/",
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_patch_update_vote_as_admin(self):
        vote_to_create = VoteFactory.build(meeting=self.meeting)

        data = {
            "question": vote_to_create.question,
        }
        response = self.admin_client.patch(
            f"/voting/admin-votes/{self.meeting.current_vote.id}/",
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, 200)

        db_vote = Vote.objects.filter(id=self.meeting.current_vote.id).first()

        self.assertEqual(db_vote.question, vote_to_create.question)

    def test_put_update_vote_as_member(self):
        vote_to_create = VoteFactory.build(meeting=self.meeting)

        data = {
            "question": vote_to_create.question,
            "open": vote_to_create.open,
            "alternatives": [],
            "meeting": self.meeting.id,
        }
        response = self.member_client.put(
            f"/voting/admin-votes/{self.meeting.current_vote.id}/",
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_put_update_vote_as_admin(self):
        vote_to_create = VoteFactory.build(meeting=self.meeting)

        data = {
            "question": vote_to_create.question,
            "open": vote_to_create.open,
            "alternatives": [],
            "meeting": self.meeting.id,
        }
        response = self.admin_client.put(
            f"/voting/admin-votes/{self.meeting.current_vote.id}/",
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, 200)

        db_vote = Vote.objects.filter(id=self.meeting.current_vote.id).first()

        self.assertEqual(db_vote.question, vote_to_create.question)
