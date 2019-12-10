import json

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient


num_users = 0

def create_user():
    user = User.objects.create_user(username=_next_username(), password='Password123')

    client = APIClient()
    client.login(username=user.username, password='Password123')

    token_response = client.get('/account/token/')
    token_data = json.loads(token_response.content.decode('utf-8'))

    client.logout()
    client.credentials(HTTP_AUTHORIZATION='JWT ' + token_data['access'])

    return user, client


def create_admin():
    #return user, client

    user = User.objects.create_superuser(username=_next_username(), email=None, password='Password123')

    client = APIClient()
    client.login(username=user.username, password='Password123')

    # vet inte om mina ändringar är vettiga
    token_response = client.get('/account/token/')
    token_data = json.loads(token_response.content.decode('utf-8'))

    client.logout()
    client.credentials(HTTP_AUTHORIZATION='JWT ' + token_data['access'])

    return user, client

def _next_username():
    global num_users
    num_users += 1
    return 'user' + str(num_users)

class AuthenticatedTestCase(TestCase):
    def setUp(self):
        self.user, self.client = create_user()
