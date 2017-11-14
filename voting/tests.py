import json

from django.test import TestCase, Client
from voting.models import Section


class SectionTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.section = Section.objects.create(name='D-sektionen')

    def test_list(self):
        response = self.client.get('/voting/sections/')

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)

        self.assertEqual(data, [{'name': self.section.name}])
