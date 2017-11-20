import json

from django.test import TestCase, Client

from account.tests import AuthenticatedTestCase, create_section, create_admin
from voting.models import Section, Meeting, Vote, Alternative


class MeetingTest(AuthenticatedTestCase):
    def test_list(self):
        section = create_section('Section')
        other_section = create_section('Other section')
        Meeting.objects.create(name='Meeting 1', section=section)
        Meeting.objects.create(name='Meeting 2', section=other_section)
        Meeting.objects.create(name='Meeting 3', section=section)

        admin, client = create_admin([section])

        response = client.get('/voting/meetings/')
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['name'], 'Meeting 1')
        self.assertEqual(data[1]['name'], 'Meeting 3')

    def test_creation(self):
        section = create_section('Section')
        admin, client = create_admin([section])

        response = client.post('/voting/meetings/', {'name': 'Meeting 1', 'section': str(section.id)})

        self.assertEqual(response.status_code, 201)


class VoteTest(AuthenticatedTestCase):
    def setUp(self):
        self.section = create_section('Section')
        self.admin, self.client = create_admin([self.section])

    def test_list(self):
        self._create_vote(self.section)

        response = self.client.get('/voting/votes/')
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['question'], 'Question?')
        self.assertEqual(data[0]['open'], True)
        self.assertEqual(len(data[0]['alternatives']), 2)
        self.assertFalse('num_votes' in data[0]['alternatives'][0])

    def test_creation(self):
        response = self.client.post('/voting/meetings/', {'name': 'Meeting 1', 'section': self.section.id})

        self.assertEqual(response.status_code, 201)

    def test_show(self):
        vote = self._create_vote(self.section)

        response = self.client.get('/voting/votes/' + str(vote.id) + '/')
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['question'], 'Question?')
        self.assertEqual(data['open'], True)
        self.assertEqual(len(data['alternatives']), 2)
        self.assertTrue('num_votes' in data['alternatives'][0])

    @staticmethod
    def _create_vote(section):
        meeting = Meeting.objects.create(name='Meeting 1', section=section)
        vote = Vote.objects.create(question='Question?', meeting=meeting)
        Alternative.objects.create(text='Alternative 1', vote=vote)
        Alternative.objects.create(text='Alternative 2', vote=vote)

        return vote
