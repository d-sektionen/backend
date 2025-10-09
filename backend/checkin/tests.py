import json
from ..account.tests.utils import AuthenticatedTestCase, create_admin, create_user
from ..checkin.models import Doorkeeper
from ..voting.models import Meeting


# Create your tests here.
class DoorkeeperTest(AuthenticatedTestCase):
    def setUp(self):
        self.admin, self.client = create_admin()

    def test_list(self):
        meeting = Meeting.objects.create(name="Meeting 100", id=1000)
        other_meeting = Meeting.objects.create(name="Meeting 2")
        Doorkeeper.objects.create(user=self.admin, event=meeting)
        Doorkeeper.objects.create(user=self.admin, event=other_meeting)

        self.client.login(username=self.admin.username, password="Password123")
        response = self.client.get(
            "/checkin/doorkeepers/",
            {"user_username": self.admin.username, "event_id": str(meeting.id)},
        )
        data = json.loads(response.content.decode("utf-8"))
        self.client.logout()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["user"]["id"], self.admin.id)
        self.assertEqual(data[0]["event"]["id"], meeting.id)

    def test_create(self):
        meeting = Meeting.objects.create(name="Meeting 1")
        Doorkeeper.objects.create(user=self.admin, event=meeting)
        user, client = create_user()

        self.client.login(username=self.admin.username, password="Password123")
        response = self.client.post(
            "/voting/attendants/?meeting_id" + str(meeting.id),
            {"user_username": user.username, "meeting_id": meeting.id},
        )
        data = json.loads(response.content.decode("utf-8"))
        self.client.logout()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data["user"]["id"], user.id)
        self.assertEqual(data["meeting"]["id"], meeting.id)

    def test_destroy(self):
        meeting = Meeting.objects.create(name="Meeting 1")
        user, user_client = create_user()
        Doorkeeper.objects.create(user=user, event=meeting)

        self.client.login(username=self.admin.username, password="Password123")
        response = self.client.get(
            "/checkin/doorkeepers/", {"username": user.username, "meeting": meeting.id}
        )
        self.client.logout()

        self.assertEqual(response.status_code, 200)
        # self.assertEqual(meeting.scanner_set.count(), 0)
