from .factories import UserFactory
from .utils import AuthenticatedTestCase
import json
from account.models import Profile


class ProfileTest(AuthenticatedTestCase):
    """Tests for endpoints under /account/profile."""

    @classmethod
    def setUpTestData(cls):
        cls.other_member = UserFactory.create()

    def test_get_own_profile(self):
        """Test that a user can get their own profile."""
        response = self.member_client.get("/account/profile/me/")

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(
            int(response_data["liu_card_id"]), self.member.profile.liu_card_id
        )

    def test_patch_own_profile(self):
        """Test that a user can PATCH update their own profile."""
        response = self.member_client.patch(
            "/account/profile/me/",
            data={"liu_card_id": self.member.profile.liu_card_id},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(
            int(response_data.get("liu_card_id")), self.member.profile.liu_card_id
        )

    def test_put_own_profile(self):
        """Test that a user can PUT update their own profile."""

        response = self.member_client.put(
            "/account/profile/me/",
            data={"liu_card_id": self.member.profile.liu_card_id},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(
            int(response_data.get("liu_card_id")), self.member.profile.liu_card_id
        )

    def test_delete_own_profile(self):
        """Test that a user cannot delete their own profile."""
        response = self.member_client.delete("/account/profile/me/")
        self.assertEqual(response.status_code, 405)

        db_profile = Profile.objects.filter(id=self.member.id).first()
        self.assertIsNotNone(db_profile)

    def test_get_other_profile(self):
        """Test that a user can get another user's profile."""
        response = self.member_client.get(f"/account/profile/{self.other_member.id}/")
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response_data["first_name"], self.other_member.first_name)

    def test_patch_other_profile(self):
        """Test that a user cannot update another user's profile."""
        response = self.member_client.patch(
            f"/account/profile/{self.other_member.id}/",
            data={"liu_card_id": self.member.profile.liu_card_id},
            format="json",
        )
        self.assertEqual(response.status_code, 405)

        db_profile = Profile.objects.filter(id=self.other_member.id).first()
        self.assertNotEqual(db_profile.liu_card_id, self.member.profile.liu_card_id)

    def test_put_other_profile(self):
        """Test that a user cannot update another user's profile."""
        response = self.member_client.put(
            f"/account/profile/{self.other_member.id}/",
            data={"liu_card_id": self.member.profile.liu_card_id},
            format="json",
        )
        self.assertEqual(response.status_code, 405)

        db_profile = Profile.objects.filter(id=self.other_member.id).first()
        self.assertNotEqual(db_profile.liu_card_id, self.member.profile.liu_card_id)

    def test_delete_other_profile(self):
        """Test that a user cannot delete another user's profile."""
        response = self.member_client.delete(
            f"/account/profile/{self.other_member.id}/"
        )
        self.assertEqual(response.status_code, 405)

        db_profile = Profile.objects.filter(id=self.other_member.id).first()
        self.assertIsNotNone(db_profile)

    def test_create_profile(self):
        """Test that a user cannot create a new profile."""
        response = self.member_client.post(
            "/account/profile/", data={"liu_card_id": 123456}, format="json"
        )
        self.assertEqual(response.status_code, 405)
        db_profile = Profile.objects.filter(liu_card_id=123456).first()
        self.assertIsNone(db_profile)

    def test_list_all_profiles(self):
        """Test that a user can get all profiles."""
        response = self.member_client.get("/account/profile/")

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(response_data), 4)
