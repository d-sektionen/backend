import json

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient


num_users = 0


# def create_section(name):
#     return Section.objects.create(name=name)


def create_user():
    user = User.objects.create_user(username=_next_username(), password='Password123')

    client = APIClient()
    client.login(username=user.username, password='Password123')

    # vet inte om mina ändringar är vettiga
    token_response = client.get('/account/token/')
    token_data = json.loads(token_response.content.decode('utf-8'))

    client.logout()
    client.credentials(HTTP_AUTHORIZATION='JWT ' + token_data['access'])

    return user, client


def create_admin():
    # TODO: should probably be a specific admin type.
    user, client = create_user()
    # TODO: Make the dude an admin.

    return user, client


def _next_username():
    global num_users
    num_users += 1
    return 'user' + str(num_users)


class AuthenticatedTestCase(TestCase):
    def setUp(self):
        self.user, self.client = create_user()


# class SectionAdministration(TestCase):
#     def setUp(self):
#         self.section = create_section('Section')
#         self.user, self.user_client = create_user([self.section])
#         self.admin, self.client = create_admin([self.section])

#     def test_transfer_ownership(self):
#         self.assertEqual(self.size_of_group(self.section.admin_group), 1)
#         self.assertTrue(self.is_in_group(self.admin, self.section.admin_group))
#         self.assertFalse(self.is_in_group(self.user, self.section.admin_group))
#         self.client.post('/account/section/', {'section': self.section.id, 'username': self.user.username})
#         self.assertEqual(self.size_of_group(self.section.admin_group), 2)
#         self.assertTrue(self.is_in_group(self.admin, self.section.admin_group))
#         self.assertTrue(self.is_in_group(self.user, self.section.admin_group))
#         self.user_client.delete('/account/section/', {'section': self.section.id, 'username': self.admin.username})
#         self.assertEqual(self.size_of_group(self.section.admin_group), 1)
#         self.assertFalse(self.is_in_group(self.admin, self.section.admin_group))
#         self.assertTrue(self.is_in_group(self.user, self.section.admin_group))

#     def size_of_group(self, group):
#         return User.objects.filter(groups__name=group.name).count()

#     def is_in_group(self, user, group):
#         return group in user.groups.all()
