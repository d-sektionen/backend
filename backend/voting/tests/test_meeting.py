import json

from ...account.tests.utils import AuthenticatedTestCase
from ..models import Meeting
from .factories import MeetingFactory


class MeetingTest(AuthenticatedTestCase):
    """Tests for endpoints under /voting/meeting and /voting/admin-meetings."""

    @classmethod
    def setUpTestData(cls):
        cls.meeting = MeetingFactory.create(open_attendance=True)
        cls.hidden_meeting = MeetingFactory.create(open_attendance=False)

    def test_list_as_member(self):
        response = self.member_client.get("/voting/meetings/")
        data = json.loads(response.content.decode("utf-8"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], self.meeting.name)

    def test_list_as_non_member(self):
        response = self.non_member_client.get("/voting/meetings/")
        self.assertEqual(response.status_code, 403)

    def test_list_specific_meeting_details_as_member(self):
        response = self.member_client.get(f"/voting/admin-meetings/{self.meeting.id}/")
        self.assertEqual(response.status_code, 403)

    def test_list_specific_meeting_details_as_admin(self):
        response = self.admin_client.get(f"/voting/admin-meetings/{self.meeting.id}/")
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content.decode("utf-8"))
        self.assertTrue("name" in response_data)
        self.assertEqual(response_data["name"], self.meeting.name)

    def test_create_meeting_as_member(self):
        meet = MeetingFactory.build()
        data = {meet.name, meet.clear_data}
        response = self.member_client.post(
            "/voting/admin-meetings/", data=data, format="json"
        )
        self.assertEqual(response.status_code, 403)

    def test_create_meeting_as_admin(self):
        meet = MeetingFactory.build()
        data = {"name": meet.name, "clear_data": meet.clear_data}
        response = self.admin_client.post(
            "/voting/admin-meetings/", data=data, format="json"
        )

        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.content.decode("utf-8"))

        created_meeting = Meeting.objects.filter(id=response_data["id"])
        self.assertEqual(len(created_meeting), 1)

    def test_patch_update_specific_meeting_details_as_member(self):
        MeetingFactory.create()  # Create separate meeting to isolate test.

        updated_meeting = MeetingFactory.build()
        data = {"name": updated_meeting.name, "clear_data": updated_meeting.clear_data}

        response = self.member_client.patch(
            f"/voting/admin-meetings/{self.meeting.id}/", data=data, format="json"
        )
        self.assertEqual(response.status_code, 403)

    def test_patch_update_specific_meeting_details_as_admin(self):
        MeetingFactory.create()  # Create separate meeting to isolate test.

        updated_meeting = MeetingFactory.build()
        data = {"name": updated_meeting.name, "clear_data": updated_meeting.clear_data}

        response = self.admin_client.patch(
            f"/voting/admin-meetings/{self.meeting.id}/", data=data, format="json"
        )
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response_data["name"], updated_meeting.name)
        self.assertEqual(response_data["clear_data"], str(updated_meeting.clear_data))

    def test_put_update_specific_meeting_details_as_member(self):
        MeetingFactory.create()  # Create separate meeting to isolate test.

        updated_meeting = MeetingFactory.build()
        data = {"name": updated_meeting.name, "clear_data": updated_meeting.clear_data}

        response = self.member_client.put(
            f"/voting/admin-meetings/{self.meeting.id}/", data=data, format="json"
        )
        self.assertEqual(response.status_code, 403)

    def test_put_update_specific_meeting_details_as_admin(self):
        MeetingFactory.create()  # Create separate meeting to isolate test.

        updated_meeting = MeetingFactory.build()
        data = {"name": updated_meeting.name, "clear_data": updated_meeting.clear_data}

        response = self.admin_client.put(
            f"/voting/admin-meetings/{self.meeting.id}/", data=data, format="json"
        )
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response_data["name"], updated_meeting.name)
        self.assertEqual(response_data["clear_data"], str(updated_meeting.clear_data))

    def test_delete_specific_meeting_as_member(self):
        created_meeting = (
            MeetingFactory.create()
        )  # Create separate meeting to isolate test.

        response = self.member_client.delete(
            f"/voting/admin-meetings/{created_meeting.id}/"
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_specific_meeting_as_admin(self):
        created_meeting = (
            MeetingFactory.create()
        )  # Create separate meeting to isolate test.

        response = self.admin_client.delete(
            f"/voting/admin-meetings/{created_meeting.id}/"
        )
        self.assertEqual(response.status_code, 405)
