import json

from django.test import TestCase

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
        meeting = Meeting.objects.create(name='Meeting 1', section=self.section)
        alternatives = [
            {
                'text': 'Alternative 1'
            },
            {
                'text': 'Alternative 2'
            }
        ]
        response = self.client.post('/voting/votes/', {'question': 'Question 1', 'meeting': meeting.id, 'alternatives': alternatives}, format='json')

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


class VotingTest(AuthenticatedTestCase):
    def setUp(self):
        self.section = create_section('Section')
        self.admin, self.client = create_admin([self.section])

        self._create_vote(self.section)

    def test_voting(self):
        response = self.client.post('/voting/made_votes/', {'vote_id': self.vote.id, 'alternative_id': self.alternative1.id})

        self.alternative1.refresh_from_db()
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.alternative1.num_votes, 1)

    def test_double_voting(self):
        response1 = self.client.post('/voting/made_votes/', {'vote_id': self.vote.id, 'alternative_id': self.alternative1.id})

        self.alternative1.refresh_from_db()
        self.assertEqual(response1.status_code, 204)
        self.assertEqual(self.alternative1.num_votes, 1)

        response2 = self.client.post('/voting/made_votes/', {'vote_id': self.vote.id, 'alternative_id': self.alternative1.id})

        self.alternative1.refresh_from_db()
        self.assertEqual(response2.status_code, 403)
        self.assertEqual(self.alternative1.num_votes, 1)

    def test_invalid_voting_request(self):
        response = self.client.post('/voting/made_votes/', {'vote_id': self.vote.id + 1, 'alternative_id': self.alternative1.id})

        self.alternative1.refresh_from_db()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.alternative1.num_votes, 0)

    def _create_vote(self, section):
        meeting = Meeting.objects.create(name='Meeting 1', section=section)
        self.vote = Vote.objects.create(question='Question?', meeting=meeting)
        self.alternative1 = Alternative.objects.create(text='Alternative 1', vote=self.vote)
        self.alternative2 = Alternative.objects.create(text='Alternative 2', vote=self.vote)


class PerfectMeeeting(TestCase):
    @classmethod
    def setUpTestData(cls):
        #cls.section = Section.objects.create(name='D-sektionen')
        #cls.users = [CreateUser(), CreateUser(), CreateUser(), CreateUser(), CreateUser()]
        #cls.admin = CreateAdmin()
        pass
        
    def test_create_meeting(self):
        # admin Skapar möte
        # Existerar mötet som just skapades
        # Tillhör den rätt sektion?
        pass

    def add_scanners(self):
        # admin lägger till två Scanners
        # finns användarna i rätt möte?
        pass
    
    def scanning_users(self):
        # scanner ska lägga till user som Attendants
        # Är users attendendats?
        pass

    def create_vote(self, name, alternatives):
        # Admin skapar omrötstning
        # Är vote i current_vote
        # Stämmer mötet överrens?
        # Stämmer svars-alternativen överens?
        pass

    def user_vote(self):
        # Varje attendent röstar på ett alternativ för current_vote
        # Läggs dom till i madeVote?
        # Stämmer number of votes för varje alternativ?
        pass
    
    def check_voting_results(self):
        # Admin stänger omröstning
        # Är current_vote closed?
        # Stämmer number of votes överens?
        pass
    
    # Call create_vote igen
    # Call user_vote
    # Call check voting results

    def close_meeting(self):
        # Admin closes meeting
        # Kolla om archived true
        pass


class BreakBeforeVote(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.section = Section.objects.create(name='D-sektionen')
        cls.users = [CreateUser(), CreateUser(), CreateUser(), CreateUser(), CreateUser()]
        cls.admin = CreateAdmin()


class BreateAfterVote(TestCase):
    pass


class ForgotLiUCard(TestCase):
    pass
