import json

from ...account.tests.utils import AuthenticatedTestCase
from ..models import Attendant
from .factories import (
    AlternativeFactory,
    AttendantFactory,
    MeetingFactory,
)

NB_OF_ATTENDANTS = 4
NB_OF_ALTERNATIVES = 4


class AttendantTest(AuthenticatedTestCase):
    """Tests for endpoints under /voting/attendants and /voting/attend."""
    @classmethod
    def setUpTestData(cls):
        cls.meeting = MeetingFactory.create(open_attendance=True)

        cls.attendants = AttendantFactory.create_batch(NB_OF_ATTENDANTS, meeting=cls.meeting)

        cls.alternatives = AlternativeFactory.create_batch(
            NB_OF_ALTERNATIVES, vote=cls.meeting.current_vote
        )

        AttendantFactory.create(meeting=cls.meeting, user=cls.member)

    def test_list_attendants_as_attending_member(self):
        response = self.member_client.get(f"/voting/attendants/?meeting_id={self.meeting.id}")

        self.assertEqual(response.status_code, 403)

    def test_list_attendants_as_admin(self):
        response = self.admin_client.get(f"/voting/attendants/?meeting_id={self.meeting.id}")

        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content.decode("utf-8"))
        db_attendant = Attendant.objects.filter(meeting=self.meeting)
        self.assertEqual(len(db_attendant), len(response_data))

    def test_self_attend_open_meeting_as_member(self):
        meeting = MeetingFactory(open_attendance=True)
        data = {"meeting_id": meeting.id}

        response = self.member_client.post("/voting/attend/", data=data, format="json")
        self.assertEqual(response.status_code, 201)

        db_attendant = Attendant.objects.filter(meeting=meeting, user=self.member)
        self.assertEqual(db_attendant.count(), 1)

    def test_self_attend_closed_meeting_as_member(self):
        meeting = MeetingFactory(open_attendance=False)
        data = {"meeting_id": meeting.id}

        response = self.member_client.post("/voting/attend/", data=data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_leave_attended_meeting_as_member(self):
        meeting = MeetingFactory(open_attendance=True)
        data = {"meeting_id": meeting.id}
        AttendantFactory.create(meeting=meeting, user=self.member)

        response = self.member_client.delete(
            f"/voting/attend/?meeting_id={meeting.id}", data=data, format="json"
        )
        self.assertEqual(response.status_code, 204)
