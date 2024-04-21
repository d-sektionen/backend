from account.tests.utils import AuthenticatedTestCase
from voting.models import Alternative
from voting.tests.factories import (
    AlternativeFactory,
    AttendantFactory,
    MadeVoteFactory,
    MeetingFactory,
    VoteFactory,
)


NB_OF_ATTENDANTS = 4
NB_OF_ALTERNATIVES = 4


class VotingTest(AuthenticatedTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.meeting = MeetingFactory.create(open_attendance=True)

        cls.attendants = AttendantFactory.create_batch(NB_OF_ATTENDANTS, meeting=cls.meeting)

        cls.alternatives = AlternativeFactory.create_batch(
            NB_OF_ALTERNATIVES, vote=cls.meeting.current_vote
        )

        VoteFactory.create(meeting=cls.meeting, open=False)
        # Make member an attendant of the meeting for these tests
        AttendantFactory.create(meeting=cls.meeting, user=cls.member)

    def test_voting_as_attending_member(self):
        meeting = MeetingFactory.create(open_attendance=True)
        alternative = AlternativeFactory.create(vote=meeting.current_vote)
        AttendantFactory.create(meeting=meeting, user=self.member)

        data = {"vote_id": meeting.current_vote.id, "alternative_id": alternative.id}
        response = self.member_client.post("/voting/made_votes/", data=data, format="json")

        self.assertEqual(response.status_code, 200)
        db_alternative = Alternative.objects.filter(id=alternative.id).first()
        self.assertEqual(db_alternative.num_votes, 1)

    def test_voting_as_unattending_member(self):
        meeting = MeetingFactory.create(open_attendance=True)
        alternative = AlternativeFactory.create(vote=meeting.current_vote)

        data = {"vote_id": meeting.current_vote.id, "alternative_id": alternative.id}
        response = self.member_client.post("/voting/made_votes/", data=data, format="json")

        self.assertEqual(response.status_code, 403)

    def test_voting_on_closed_vote_as_attending_member(self):
        meeting = MeetingFactory.create(open_attendance=True)
        meeting.current_vote = VoteFactory(open=False, meeting=meeting)
        alternative = AlternativeFactory.create(vote=meeting.current_vote)
        AttendantFactory.create(meeting=meeting, user=self.member)

        data = {"vote_id": meeting.current_vote.id, "alternative_id": alternative.id}
        response = self.member_client.post("/voting/made_votes/", data=data, format="json")

        self.assertEqual(response.status_code, 403)

    def test_voting_on_closed_meeting_as_attending_member(self):
        meeting = MeetingFactory.create(open_attendance=False)
        alternative = AlternativeFactory.create(vote=meeting.current_vote)
        AttendantFactory.create(meeting=meeting, user=self.member)

        data = {"vote_id": meeting.current_vote.id, "alternative_id": alternative.id}
        response = self.member_client.post("/voting/made_votes/", data=data, format="json")

        self.assertEqual(response.status_code, 200)
        db_alternative = Alternative.objects.filter(id=alternative.id).first()
        self.assertEqual(db_alternative.num_votes, 1)

    def test_voting_on_closed_meeting_as_unattending_member(self):
        meeting = MeetingFactory.create(open_attendance=False)
        alternative = AlternativeFactory.create(vote=meeting.current_vote)

        data = {"vote_id": meeting.current_vote.id, "alternative_id": alternative.id}
        response = self.member_client.post("/voting/made_votes/", data=data, format="json")

        self.assertEqual(response.status_code, 403)

    def test_delete_made_vote_as_member(self):
        meeting = MeetingFactory.create(open_attendance=False)
        alternative = AlternativeFactory.create(vote=meeting.current_vote)
        AttendantFactory.create(meeting=meeting, user=self.member)

        data = {"vote_id": meeting.current_vote.id, "alternative_id": alternative.id}
        response = self.member_client.delete("/voting/made_votes/", data=data, format="json")

        self.assertEqual(response.status_code, 405)

    def test_vote_twice_as_member(self):
        meeting = MeetingFactory.create(open_attendance=False)
        alternative = AlternativeFactory.create(vote=meeting.current_vote)
        AttendantFactory.create(meeting=meeting, user=self.member)
        MadeVoteFactory.create(user=self.member, vote=meeting.current_vote)

        data = {"vote_id": meeting.current_vote.id, "alternative_id": alternative.id}
        response = self.member_client.post("/voting/made_votes/", data=data, format="json")

        self.assertEqual(response.status_code, 403)
