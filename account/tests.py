from django.contrib.auth.models import User
from django.test import TestCase, Client


class AuthenticatedTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.username = 'testuser'
        cls.password = 'Password123'
        cls.user = User.objects.create_user(username=cls.username, password=cls.password)

    def setUp(self):
        self.client = Client()
        self.client.login(username=self.username, password=self.password)
