import json

from django.test import TestCase

from account.tests import AuthenticatedTestCase, create_section, create_admin, create_user
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


class BasicTest(AuthenticatedTestCase):
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


class PerfectMeeeting(TestCase):
    @classmethod
    def setUpTestData(cls):
        section = 'D-sektionen'
        cls.section = create_section(name=section)
        cls.users = [create_user([cls.section]) for _ in range(5)]
        cls.scanners = [create_user([cls.section]) for _ in range(2)]
        cls.admin = create_admin([cls.section])
    
    def test_creation(self):
        section = create_section('Section')
        admin, client = create_admin([section])

        response = client.post('/voting/meetings/', {'name': 'Meeting 1', 'section': str(section.id)})
        self.assertEqual(response.status_code, 201)

    def test_perfect_meeting(self):
        meeting_name = 'Meeting 1'
        create_response = self.admin[1].post('/voting/meetings/', {'name': meeting_name, 'section': self.section.id})        
        self.assertEqual(create_response.status_code, 201)

        meeting_id = json.loads(create_response.content.decode('utf-8'))['id']
        
        for scanner in self.scanners:
            scanner_res = self.admin[1].post('/voting/scanners/', {'user': scanner[0].id, 'meeting': meeting_id})
            self.assertEqual(scanner_res.status_code, 201)
    
        # Scan in all users
        for user in self.users:
            attendant_res = self.scanners[1][1].post('/voting/attendants/', {'user': user[0].id, 'meeting': meeting_id})
            self.assertEqual(attendant_res.status_code, 201)

        # Create vote
        vote_res = self.admin[1].post('/voting/votes/', {'question': 'Vilken är den bästa sektionen här?', 'open': True, 'alternatives': ['D', 'Y']})
        print(json.loads())        
        self.assertEqual(vote_res.status_code, 201)

        # Test if the /voting/meetings/ works correctly
        #list_response = self.admin.get('/voting/meetings/').json()
        #self.assertContains(list_response, meeting_name)

        # Test if the /voting/meetings/id
        #meeting_response = self.admin.get('/voting/meetings/' + create_response.id).json()
        #self.assertEqual(meeting_response, create_response)



"""class BreakBeforeVote(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.section = Section.objects.create(name='D-sektionen')
        cls.users = [CreateUser(), CreateUser(), CreateUser(), CreateUser(), CreateUser()]
        cls.admin = CreateAdmin()


class BreateAfterVote(TestCase):
    pass


class ForgotLiUCard(TestCase):
    pass
"""