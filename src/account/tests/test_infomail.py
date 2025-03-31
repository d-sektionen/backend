from .factories import UserFactory
from .utils import AuthenticatedTestCase
import json
from account.models import Profile


class InfomailTest(AuthenticatedTestCase):
    """Tests for endpoints /account/infomail-*."""

    @classmethod
    def setUpTestData(cls):
        cls.other_admin_member = UserFactory.create(admin=True)
        cls.other_admin_member.profile.infomail_subscriber = False
        cls.other_admin_member.profile.save()

    def lookup_user(self, data, id):
        found_user = False
        for user in data:
            if user.get("id") == id:
                found_user = True
                break

        return found_user

    def test_get_infomail_subscribers(self):
        """Test that an admin can get all infomail subscribers."""
        response = self.admin_client.get("/account/infomail-subscribers/")

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content.decode("utf-8"))

        self.assertTrue(self.lookup_user(response_data, self.admin.id))

    def test_get_infomail_subscribers_not_subscribing(self):
        """Test that unsubscribed users are not included in the list of subscribers."""
        response = self.admin_client.get("/account/infomail-subscribers/")

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content.decode("utf-8"))

        self.assertFalse(self.lookup_user(response_data, self.other_admin_member.id))

    def test_get_infomail_subscribers_as_non_admin(self):
        """Test that a non-admin user cannot get the list of infomail subscribers."""
        response = self.member_client.get("/account/infomail-subscribers/")
        self.assertEqual(response.status_code, 403)

        response = self.non_member_client.get("/account/infomail-subscribers/")
        self.assertEqual(response.status_code, 403)

    def test_get_infomail_everyone_as_admin(self):
        response = self.admin_client.get("/account/infomail-everyone/")

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content.decode("utf-8"))

        len_profiles_from_db = Profile.objects.all().count()
        self.assertEqual(len(response_data), len_profiles_from_db)

    def test_get_infomail_everyone_as_non_admin(self):
        """Test that a non-admin user cannot get the list of all users."""
        response = self.member_client.get("/account/infomail-everyone/")
        self.assertEqual(response.status_code, 403)

        response = self.non_member_client.get("/account/infomail-everyone/")
        self.assertEqual(response.status_code, 403)
