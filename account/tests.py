import json

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from voting.models import Section

num_users = 0


def create_section(name):
    return Section.objects.create(name=name)


def create_user(add_to_sections=None):
    user = User.objects.create_user(username=_next_username(), password='Password123')
    if add_to_sections:
        for section in add_to_sections:
            user.groups.add(section.user_group)

    client = APIClient()
    client.login(username=user.username, password='Password123')

    token_response = client.get('/account/token')
    token_data = json.loads(token_response.content.decode('utf-8'))

    client.logout()
    client.credentials(HTTP_AUTHORIZATION='JWT ' + token_data['token'])

    return user, client


def create_admin(add_to_sections):
    user, client = create_user(add_to_sections)
    for section in add_to_sections:
        user.groups.add(section.admin_group)

    return user, client


def _next_username():
    global num_users
    num_users += 1
    return 'user' + str(num_users)


class AuthenticatedTestCase(TestCase):
    def setUp(self):
        self.user, self.client = create_user()
