import json

from django.test import TestCase, Client

from account.tests import AuthenticatedTestCase, create_section, create_admin
from voting.models import Section


class MeetingTest(AuthenticatedTestCase):
    def test_creation(self):
        section = create_section('Section')
        admin, client = create_admin([section])

        response = client.post('/voting/meetings/', {'name': 'Meeting 1', 'section': str(section.id)})

        self.assertEqual(response.status_code, 201)
