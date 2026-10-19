from rest_framework.test import APIClient, APITestCase

from ...account.tests.factories import UserFactory
from ...membership.tests.factories import MemberFactory


class AuthenticatedTestCase(APITestCase):
    """Intended to be inherited from. Sets up three level of users on the class:
    - non_member: Has only the permissions of someone who's not a member of the section.
    - member: Has all permissions a member of the section has.
    - admin: Has all permissions (superuser).
    """

    @classmethod
    def setUpClass(cls):
        # User with no privileges
        cls.non_member = UserFactory()
        cls.non_member_client = APIClient()
        cls.non_member_client.force_authenticate(cls.non_member)

        # User with membership privileges
        cls.member = UserFactory()
        cls.member_membership = MemberFactory.create(  # type: ignore[attr-defined]
            liu_id=cls.member.username, membership_type="S"
        )
        cls.member_client = APIClient()
        cls.member_client.force_authenticate(cls.member)

        # Admin user
        cls.admin = UserFactory.create(admin=True)  # type: ignore[attr-defined]
        cls.admin_membership = MemberFactory.create(
            liu_id=cls.admin.username, membership_type="S"
        )  # type: ignore[attr-defined]
        cls.admin_client = APIClient()
        cls.admin_client.force_authenticate(cls.admin)

        return super().setUpClass()
