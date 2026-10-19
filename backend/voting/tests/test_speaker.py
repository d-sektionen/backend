from ...account.tests.utils import AuthenticatedTestCase
from .factories import (
    AttendantFactory,
    MeetingFactory,
)


class SpeakerTest(AuthenticatedTestCase):
    """Tests for endpoints under /voting/speakers."""

    @classmethod
    def setUpTestData(cls):
        cls.meeting = MeetingFactory.create(open_attendance=True)
        AttendantFactory.create(meeting=cls.meeting, user=cls.member)

    def test_request_to_speak_as_member(self):
        data = {"meeting_id": self.meeting.id, "prioritized": True}
        response = self.member_client.post(
            f"/voting/speakers/?meeting_id={self.meeting.id}", data=data, format="json"
        )

        self.assertEqual(response.status_code, 201)

    def test_remove_from_speak_as_member(self):
        data = {"meeting_id": self.meeting.id, "prioritized": True}
        response = self.member_client.post(
            f"/voting/speakers/?meeting_id={self.meeting.id}", data=data, format="json"
        )

        self.assertEqual(response.status_code, 201)

    def test_request_to_speak_as_non_attending_member(self):
        meeting = MeetingFactory.create()
        data = {"meeting_id": meeting.id, "prioritized": True}
        response = self.member_client.post(
            f"/voting/speakers/?meeting_id={self.meeting.id}", data=data, format="json"
        )

        self.assertEqual(response.status_code, 400)
