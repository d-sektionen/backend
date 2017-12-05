import json

from django.test import TestCase

from account.tests import AuthenticatedTestCase, create_section, create_admin, create_user
from voting.models import Section, Meeting, Vote, Alternative, Scanner, Attendant


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

    def test_create(self):
        section = create_section('Section')
        admin, client = create_admin([section])

        response = client.post('/voting/meetings/', {'name': 'Meeting 1', 'section': str(section.id)})
        self.assertEqual(response.status_code, 201)

    def test_show(self):
        section = create_section('Section')
        meeting = Meeting.objects.create(name='Meeting 1', section=section)
        admin, client = create_admin([section])

        response = client.get('/voting/meetings/' + str(meeting.id) + '/')
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['name'], 'Meeting 1')
        self.assertEqual(data['current_vote'], None)
        self.assertEqual(data['section'], section.id)
        self.assertEqual(data['archived'], False)

    def test_update(self):
        section = create_section('Section')
        meeting = Meeting.objects.create(name='Meeting 1', section=section)
        admin, client = create_admin([section])

        response = client.patch('/voting/meetings/' + str(meeting.id) + '/', {'name': 'New meeting name', 'archived': True})
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['name'], 'New meeting name')
        self.assertEqual(data['archived'], True)


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

    def test_update(self):
        vote = self._create_vote(self.section)

        # Ensure that the number of votes persist
        alternatives = vote.alternative_set.all()
        first_alternative = alternatives[0]
        first_alternative.num_votes = 15
        first_alternative.save()
        second_alternative = alternatives[1]
        second_alternative.num_votes = 7
        second_alternative.save()

        patch_data = {
            'question': 'New question',
            'alternatives': [
                {
                    'id': first_alternative.id,
                    'text': 'New alternative 1'
                },
                {
                    'id': second_alternative.id
                }
            ]
        }
        response = self.client.patch('/voting/votes/' + str(vote.id) + '/', patch_data, format='json')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/voting/votes/' + str(vote.id) + '/')
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(data['question'], 'New question')
        self.assertEqual(data['open'], True)
        self.assertEqual(len(data['alternatives']), 2)
        self.assertEqual(data['alternatives'][0]['text'], 'New alternative 1')
        self.assertEqual(data['alternatives'][1]['text'], 'Alternative 2')
        self.assertEqual(data['alternatives'][0]['num_votes'], 15)
        self.assertEqual(data['alternatives'][1]['num_votes'], 7)

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


class ScannerTest(AuthenticatedTestCase):
    def test_list(self):
        section = create_section('Section')
        meeting = Meeting.objects.create(name='Meeting 1', section=section)
        other_meeting = Meeting.objects.create(name='Meeting 1', section=section)
        user, user_client = create_user([section])
        Scanner.objects.create(user=user, meeting=meeting)
        Scanner.objects.create(user=user, meeting=other_meeting)

        response = self.client.get('/voting/scanners/?meeting=' + str(meeting.id))
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['user'], user.id)
        self.assertEqual(data[0]['meeting']['id'], meeting.id)

    def test_create(self):
        section = create_section('Section')
        meeting = Meeting.objects.create(name='Meeting 1', section=section)
        user, user_client = create_user([section])

        response = self.client.post('/voting/scanners/', {'username': user.username, 'meeting': meeting.id})
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['user'], user.id)
        self.assertEqual(data['meeting']['id'], meeting.id)

    def test_destroy(self):
        section = create_section('Section')
        meeting = Meeting.objects.create(name='Meeting 1', section=section)
        user, user_client = create_user([section])
        Scanner.objects.create(user=user, meeting=meeting)

        response = self.client.delete('/voting/scanners/', {'username': user.username, 'meeting': meeting.id})
        self.assertEqual(response.status_code, 204)
        self.assertEqual(meeting.scanner_set.count(), 0)


class AttendantTest(AuthenticatedTestCase):
    def test_list(self):
        section = create_section('Section')
        meeting = Meeting.objects.create(name='Meeting 1', section=section)
        other_meeting = Meeting.objects.create(name='Meeting 1', section=section)
        user, user_client = create_user([section])
        Attendant.objects.create(user=user, meeting=meeting)
        Attendant.objects.create(user=user, meeting=other_meeting)

        response = self.client.get('/voting/attendants/?meeting=' + str(meeting.id))
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['user'], user.id)
        self.assertEqual(data[0]['meeting'], meeting.id)

    def test_create(self):
        section = create_section('Section')
        meeting = Meeting.objects.create(name='Meeting 1', section=section)
        user, user_client = create_user([section])

        response = self.client.post('/voting/attendants/', {'username': user.username, 'meeting': meeting.id})
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['user'], user.id)
        self.assertEqual(data['meeting'], meeting.id)

    def test_destroy(self):
        section = create_section('Section')
        meeting = Meeting.objects.create(name='Meeting 1', section=section)
        user, user_client = create_user([section])
        Attendant.objects.create(user=user, meeting=meeting)

        response = self.client.delete('/voting/attendants/', {'username': user.username, 'meeting': meeting.id})
        self.assertEqual(response.status_code, 204)
        self.assertEqual(meeting.attendant_set.count(), 0)


class PerfectMeeeting(TestCase):
    @classmethod
    def setUpTestData(cls):
        section = 'D-sektionen'
        cls.section = create_section(name=section)
        cls.users = [create_user([cls.section]) for _ in range(5)]
        cls.scanners = [create_user([cls.section]) for _ in range(2)]
        cls.admin = create_admin([cls.section])
        

    def parse(self, response):
        return json.loads(response.content.decode('utf-8'))


    def test_creation(self):
        section = create_section('Section')
        admin, client = create_admin([section])

        response = client.post('/voting/meetings/', {'name': 'Meeting 1', 'section': str(section.id)})
        self.assertEqual(response.status_code, 201)


    def test_perfect_meeting(self):       
        create_res = self.admin[1].post('/voting/meetings/', {'name': 'Meeting 1', 'section': self.section.id})        
        self.assertEqual(create_res.status_code, 201)

        meeting_id = self.parse(create_res)['id']
        
        # Add scanners
        for scanner in self.scanners:
            scanner_res = self.admin[1].post('/voting/scanners/', {'username': scanner[0].username, 'meeting': meeting_id})
            self.assertEqual(scanner_res.status_code, 201)
    
        # Scanners scan all users
        for user in self.users:
            attendant_res = self.scanners[1][1].post('/voting/attendants/', {'username': user[0].username, 'meeting': meeting_id})
            self.assertEqual(attendant_res.status_code, 201)

			
        # Do two votes for some reason
        for _ in range(2):
            # Create vote
            alternatives = [{'text': 'D'}, {'text': 'Y'}]
            vote_res = self.admin[1].post('/voting/votes/', {'question': 'Vilken är den bästa sektionen här?', 'meeting': meeting_id, 'alternatives': alternatives}, format='json')
            self.assertEqual(vote_res.status_code, 201)

            vote_json = self.parse(vote_res)
            alternatives = [alt['id'] for alt in vote_json['alternatives']]

            # One user votes for Y 
            uservote_res = self.users[0][1].post('/voting/made_votes/', {'vote_id': vote_json['id'], 'alternative_id': alternatives[1]})
            self.assertEqual(uservote_res.status_code, 204)
                
            # The rest votes for the obvoius choice: D 
            for user in self.users[1:]:
                uservote_res =  user[1].post('/voting/made_votes/', {'vote_id': vote_json['id'], 'alternative_id': alternatives[0]})
                self.assertEqual(uservote_res.status_code, 204)
                    
            # Close the vote
            close_res = self.admin[1].patch('/voting/votes/'+str(vote_json['id'])+'/', {'open': False}, format='json')
            self.assertEqual(close_res.status_code, 200)
            self.assertEqual(self.parse(close_res)['open'], False)

            # Count the votes
            result_res = self.admin[1].get('/voting/votes/'+str(vote_json['id'])+'/')
            self.assertEqual(result_res.status_code, 200)
            
            for result in self.parse(result_res)['alternatives']:
                if result['text'] == 'D':
                    self.assertEqual(result['num_votes'], 4) # WOHO WE WON!!!
                else:
                    self.assertEqual(result['num_votes'], 1)

        # delete this
        delete_res = self.admin[1].delete('/voting/meetings/{}/'.format(meeting_id))
        self.assertEqual(delete_res.status_code, 204)


class BreakBeforeVote(TestCase):
    @classmethod
    def setUpTestData(cls):
        section = 'D-sektionen'
        cls.section = create_section(name=section)
        cls.users = [create_user([cls.section]) for _ in range(2)]
        cls.scanner = create_user([cls.section])
        cls.admin, cls.admin_client = create_admin([cls.section])

    def parse(self, response):
        return json.loads(response.content.decode('utf-8'))

    def test_leave(self):
        meeting_response = self.admin_client.post('/voting/meetings/', {'name': 'Meeting 1', 'section': str(self.section.id)})
        meeting_id = self.parse(meeting_response)['id']

        alternatives = [{'text': 'D'}, {'text': 'Y'}]
        vote_res = self.admin_client.post('/voting/votes/', {'question': 'Vilken är den bästa sektionen här?', 'meeting': meeting_id, 'alternatives': alternatives}, format='json')
        vote_json = self.parse(vote_res)
        self.admin_client.post('/voting/attendants/', {'username': self.users[0][0].username, 'meeting': meeting_id})
        attendant_response = self.admin_client.post('/voting/attendants/', {'username': self.users[1][0].username, 'meeting': meeting_id})
        self.assertEqual(attendant_response.status_code, 201)

        alternatives = [alt['id'] for alt in vote_json['alternatives']]

        user_drop_response = self.admin_client.delete('/voting/attendants/', {'username': self.users[1][0].username, 'meeting': meeting_id})
        self.assertEqual(user_drop_response.status_code, 204)
        self.users[1][1].post('/voting/made_votes/', {'vote_id': vote_json['id'], 'alternative_id': alternatives[0]})
        uservote_res = self.users[0][1].post('/voting/made_votes/', {'vote_id': vote_json['id'], 'alternative_id': alternatives[0]})
        self.assertEqual(uservote_res.status_code, 204)
        
class BreakAfterVote(TestCase):
    @classmethod
    def setUpTestData(cls):
        section = 'D-sektionen'
        cls.section = create_section(name=section)
        cls.user, cls.user_client = create_user([cls.section])
        cls.scanner, cls.scanner_client  = create_user([cls.section])
        cls.admin, cls.admin_client = create_admin([cls.section])

    def parse(self, response):
        return json.loads(response.content.decode('utf-8'))

    def test_leave(self):
        meeting_response = self.admin_client.post('/voting/meetings/', {'name': 'Meeting 1', 'section': str(self.section.id)})
        meeting_id = self.parse(meeting_response)['id']
        
        alternatives = [{'text': 'D'}, {'text': 'Y'}]
        vote_res = self.admin_client.post('/voting/votes/', {'question': 'Vilken är den bästa sektionen här?', 'meeting': meeting_id, 'alternatives': alternatives}, format='json')
        self.admin_client.post('/voting/scanners/', {'user': self.scanner.id, 'meeting': meeting_id})
        
        vote_json = self.parse(vote_res)
        alternatives = [alt['id'] for alt in vote_json['alternatives']]
        
        self.scanner_client.post('/voting/attendants/', {'username': self.user.username, 'meeting': meeting_id})
        uservote_res = self.user_client.post('/voting/made_votes/', {'vote_id': vote_json['id'], 'alternative_id': alternatives[0]})
        self.assertEqual(uservote_res.status_code, 204)

        user_drop_response = self.scanner_client.delete('/voting/attendants/', {'username': self.user.username, 'meeting': meeting_id})
        self.assertEqual(user_drop_response.status_code, 204)

        self.scanner_client.post('/voting/attendants/', {'username': self.user.username, 'meeting': meeting_id})
        uservote_fail_res = self.user_client.post('/voting/made_votes/', {'vote_id': vote_json['id'], 'alternative_id': alternatives[0]})
        self.assertEqual(uservote_fail_res.status_code, 403)

class ForgotLiUCard(TestCase):
    @classmethod
    def setUpTestData(cls):
        section = 'D-sektionen'
        cls.section = create_section(name=section)
        cls.user, cls.user_client = create_user([cls.section])
        cls.admin, cls.admin_client = create_admin([cls.section])

    def parse(self, response):
        return json.loads(response.content.decode('utf-8'))

    def test_leave(self):
        meeting_response = self.admin_client.post('/voting/meetings/', {'name': 'Meeting 1', 'section': str(self.section.id)})
        meeting_id = self.parse(meeting_response)['id']
        
        self.admin_client.post('/voting/attendants/', {'id': self.user.id, 'meeting': meeting_id})

        alternatives = [{'text': 'D'}, {'text': 'TBI'}]
        vote_res = self.admin_client.post('/voting/votes/', {'question': 'Vilken är den bästa sektionen här?', 'meeting': meeting_id, 'alternatives': alternatives}, format='json')
        
        vote_json = self.parse(vote_res)
        alternatives = [alt['id'] for alt in vote_json['alternatives']]
        
        uservote_res = self.user_client.post('/voting/made_votes/', {'vote_id': vote_json['id'], 'alternative_id': alternatives[0]})
        self.assertEqual(uservote_res.status_code, 204)
       
        result_res = self.admin_client.get('/voting/votes/'+str(vote_json['id'])+'/')
        self.assertEqual(result_res.status_code, 200)
        
        for result in self.parse(result_res)['alternatives']:
            if result['text'] == 'D':
                self.assertEqual(result['num_votes'], 1) # WOHO WE WON!!!
            else:
                self.assertEqual(result['num_votes'], 0)

class WrongSection(TestCase):
    @classmethod
    def setUpTestData(cls):
        section = 'D-sektionen'
        cls.section = create_section(name=section)
        cls.section2 = create_section(name="Test-sektionen")
        cls.scanner, cls.scanner_client = create_user([cls.section2])
        cls.user, cls.user_client = create_user([cls.section])
        cls.admin, cls.admin_client = create_admin([cls.section])

    def parse(self, response):
        return json.loads(response.content.decode('utf-8'))

    def test_wrong_section(self):
        # Create meeting
        meeting_response = self.admin_client.post('/voting/meetings/', {'name': 'Meeting 1', 'section': str(self.section.id)})
        meeting_id = self.parse(meeting_response)['id']
        
        # Make Scanner
        scanner_res = self.admin_client.post('/voting/scanners/', {'username': self.scanner.username, 'meeting': meeting_id})
        self.assertEqual(scanner_res.status_code, 201)

        # Add legitimate user (for dev.check only, remove once this test is working)
        add_user_response = self.scanner_client.post('/voting/attendants/', {'username': self.user.username, 'meeting': meeting_id})
        self.assertEqual(add_user_response.status_code, 201)

        #Scanner adds himself, should fail since scanner is member of the wrong section
        add_user_fail_response = self.scanner_client.post('/voting/attendants/', {'username': self.scanner.username, 'meeting': meeting_id})
        
        self.assertEqual(add_user_fail_response.status_code, 403)
        attendants_response = self.admin_client.get('/voting/attendants/', {'meeting': meeting_id})
        
        #for attendant in self.parse(attendants_response):
            #print(attendant)

class PizzaBreak(TestCase):
    @classmethod
    def setUpTestData(cls):
        section = 'D-sektionen'
        cls.section = create_section(name=section)
        cls.scanner, cls.scanner_client = create_user([cls.section])
        cls.users = [create_user([cls.section]) for _ in range(50)]
        cls.admin, cls.admin_client = create_admin([cls.section])

    def parse(self, response):
        return json.loads(response.content.decode('utf-8'))

    def test_pizza_break(self):
        # Create meeting
        meeting_response = self.admin_client.post('/voting/meetings/', {'name': 'Meeting 1', 'section': str(self.section.id)})
        meeting_id = self.parse(meeting_response)['id']
      
        # Make Scanner
        scanner_res = self.admin_client.post('/voting/scanners/', {'username': self.scanner.username, 'meeting': meeting_id})
        self.assertEqual(scanner_res.status_code, 201)

        # Create first vote
        alternatives = [{'text': 'D'}, {'text': 'Ling'}]
        vote_res = self.admin_client.post('/voting/votes/', {'question': 'Vilken är den bästa sektionen här?', 'meeting': meeting_id, 'alternatives': alternatives}, format='json')
        
        vote_json = self.parse(vote_res)
        alternatives = [alt['id'] for alt in vote_json['alternatives']]

        # Add attendants, attendant votes on first vote immediately
        for user in self.users:
            self.scanner_client.post('/voting/attendants/', {'username': user[0].username, 'meeting': meeting_id})
            user[1].post('/voting/made_votes/', {'vote_id': vote_json['id'], 'alternative_id': alternatives[0]})

        # Close first vote
        self.admin_client.patch('/voting/votes/'+str(vote_json['id'])+'/', {'open': False}, format='json')

        # Check result of first vote
        result_res = self.admin_client.get('/voting/votes/'+str(vote_json['id'])+'/')
        for result in self.parse(result_res)['alternatives']:
            if result['text'] == 'D':
                self.assertEqual(result['num_votes'], 50) # WOHO WE WON!!!
            else:
                self.assertEqual(result['num_votes'], 0)

        # Remove all users from the meeting
        for user in self.users:
            self.scanner_client.delete('/voting/attendants/', {'username': user[0].username, 'meeting': meeting_id})
        
        # Create second vote
        alternatives = [{'text': 'Två maskinare'}, {'text': 'En IT:are'}]
        vote_res = self.admin_client.post('/voting/votes/', {'question': 'En maskinare, en maskinare. Finns det nånting finare? Finns det nånting finare så är det', 'meeting': meeting_id, 'alternatives': alternatives}, format='json')
        
        vote_json = self.parse(vote_res)
        alternatives = [alt['id'] for alt in vote_json['alternatives']]
        
        # Add the second half of users to the meeting and vote on second vote
        for user in self.users[25:]:
            self.scanner_client.post('/voting/attendants/', {'username': user[0].username, 'meeting': meeting_id})
            user[1].post('/voting/made_votes/', {'vote_id': vote_json['id'], 'alternative_id': alternatives[1]})

        # Close second vote
        self.admin_client.patch('/voting/votes/'+str(vote_json['id'])+'/', {'open': False}, format='json')
   
        # Check result of second vote
        result_res = self.admin_client.get('/voting/votes/'+str(vote_json['id'])+'/')
        for result in self.parse(result_res)['alternatives']:
            if result['text'] == 'En IT:are':
                self.assertEqual(result['num_votes'], 25) # WOHO WE WON!!!
            else:
                self.assertEqual(result['num_votes'], 0)

class NoDuplicates(AuthenticatedTestCase):
    def setUp(self):
        self.section = create_section('Section')
        self.meeting = Meeting.objects.create(name='Meeting 1', section=self.section)
        self.user, self.user_client = create_user([self.section])
        self.admin, self.client = create_admin([self.section])

    def test_duplicate_scanner(self):
        scanner_res = self.client.post('/voting/scanners/', {'username': self.user.username, 'meeting': self.meeting.id})
        self.assertEqual(scanner_res.status_code, 201)

        scanner_res = self.client.post('/voting/scanners/', {'username': self.user.username, 'meeting': self.meeting.id})
        self.assertEqual(scanner_res.status_code, 400)

    def test_duplicate_attendant(self):
        Scanner.objects.create(user=self.user, meeting=self.meeting)

        attendant, attendant_client = create_user([self.section])
        attendant_res = self.user_client.post('/voting/attendants/', {'username': attendant.username, 'meeting': self.meeting.id})
        self.assertEqual(attendant_res.status_code, 201)

        attendant_res = self.user_client.post('/voting/attendants/', {'username': attendant.username, 'meeting': self.meeting.id})
        self.assertEqual(attendant_res.status_code, 400)

