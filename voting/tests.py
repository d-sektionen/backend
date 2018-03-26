import json

from channels.test import ChannelTestCase, WSClient
from django.contrib.auth.models import User
from django.test import TestCase

from account.tests import AuthenticatedTestCase, create_section, create_admin, create_user
from voting.models import Section, Meeting, Vote, Alternative, Scanner, Attendant, MadeVote


# --- Reoccurring operations ---
def parse(response):
        return json.loads(response.content.decode('utf-8'))

def admin_create_meeting(self, admin_client, section_id):
            create_res = admin_client.post('/voting/meetings/', {'name': 'Meeting 1', 'section': section_id})
            self.assertEqual(create_res.status_code, 201)

def admin_close_vote(self, vote):
                vote_id = parse(self.admin_client.get('/voting/votes/'))[vote]['id']
                close_res = self.admin_client.patch('/voting/votes/'+str(vote_id)+'/', {'open': False}, format='json')
                self.assertEqual(close_res.status_code, 200)
                self.assertEqual(parse(close_res)['open'], False)

def attendant_votes(self, vote, alternative, voter_client):
                vote_obj = parse(voter_client.get('/voting/votes/?current=true'))[vote]
                vote_id = vote_obj['id']
                alternative_id = vote_obj['alternatives'][alternative]['id']
                uservote_res = voter_client.post('/voting/made_votes/', {'vote_id': vote_id, 'alternative_id': alternative_id})
                self.assertEqual(uservote_res.status_code, 200)
# --- ---------------------- ---
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
        self.assertEqual(data['section']['id'], section.id)
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
        self.other_section = create_section('Other section')
        self.admin, self.client = create_admin([self.section])

    def test_list(self):
        vote, meeting = self._create_vote(self.section)
        self._create_vote(self.other_section)

        Attendant.objects.create(meeting=meeting, user=self.admin)

        response = self.client.get('/voting/votes/')
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)  # Should only return the open votes of the meeting the user attends!
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
        vote, meeting = self._create_vote(self.section)

        Attendant.objects.create(meeting=meeting, user=self.admin)

        response = self.client.get('/voting/votes/' + str(vote.id) + '/')
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['question'], 'Question?')
        self.assertEqual(data['open'], True)
        self.assertEqual(len(data['alternatives']), 2)
        self.assertTrue('num_votes' in data['alternatives'][0])

    def test_update(self):
        vote, meeting = self._create_vote(self.section)

        Attendant.objects.create(meeting=meeting, user=self.admin)

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

        return vote, meeting


class VotingTest(AuthenticatedTestCase):
    def setUp(self):
        self.section = create_section('Section')
        self.admin, self.client = create_admin([self.section])

        self._create_vote(self.section)

    def test_voting(self):
        response = self.client.post('/voting/made_votes/', {'vote_id': self.vote.id, 'alternative_id': self.alternative1.id})

        self.alternative1.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.alternative1.num_votes, 1)

    def test_double_voting(self):
        response1 = self.client.post('/voting/made_votes/', {'vote_id': self.vote.id, 'alternative_id': self.alternative1.id})

        self.alternative1.refresh_from_db()
        self.assertEqual(response1.status_code, 200)
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
        Attendant.objects.create(meeting=meeting, user=self.admin)


class ScannerTest(AuthenticatedTestCase):
    def setUp(self):
        self.section = create_section('Section')
        self.admin, self.client = create_admin([self.section])

    def test_list(self):
        meeting = Meeting.objects.create(name='Meeting 1', section=self.section)
        other_meeting = Meeting.objects.create(name='Meeting 1', section=self.section)
        user, user_client = create_user([self.section])
        Scanner.objects.create(user=user, meeting=meeting)
        Scanner.objects.create(user=user, meeting=other_meeting)

        response = self.client.get('/voting/scanners/?meeting=' + str(meeting.id))
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['user']['id'], user.id)
        self.assertEqual(data[0]['meeting']['id'], meeting.id)

    def test_create(self):
        meeting = Meeting.objects.create(name='Meeting 1', section=self.section)
        user, user_client = create_user([self.section])

        response = self.client.post('/voting/scanners/', {'username': user.username, 'meeting': meeting.id})
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['user']['id'], user.id)
        self.assertEqual(data['meeting']['id'], meeting.id)

    def test_destroy(self):
        meeting = Meeting.objects.create(name='Meeting 1', section=self.section)
        user, user_client = create_user([self.section])
        Scanner.objects.create(user=user, meeting=meeting)

        response = self.client.delete('/voting/scanners/', {'username': user.username, 'meeting': meeting.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(meeting.scanner_set.count(), 0)


class AttendantTest(AuthenticatedTestCase):

    def setUp(self):
        self.section = create_section('Section')
        self.admin, self.client = create_admin([self.section])

    def test_list(self):
        meeting = Meeting.objects.create(name='Meeting 1', section=self.section)
        other_meeting = Meeting.objects.create(name='Meeting 1', section=self.section)
        user, user_client = create_user([self.section])
        Attendant.objects.create(user=user, meeting=meeting)
        Attendant.objects.create(user=user, meeting=other_meeting)

        response = self.client.get('/voting/attendants/?meeting=' + str(meeting.id))
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['user']['id'], user.id)
        self.assertEqual(data[0]['meeting'], meeting.id)

    def test_create(self):
        meeting = Meeting.objects.create(name='Meeting 1', section=self.section)
        user, user_client = create_user([self.section])

        response = self.client.post('/voting/attendants/', {'username': user.username, 'meeting': meeting.id})
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['user']['id'], user.id)
        self.assertEqual(data['meeting'], meeting.id)

    def test_destroy(self):
        meeting = Meeting.objects.create(name='Meeting 1', section=self.section)
        user, user_client = create_user([self.section])
        Attendant.objects.create(user=user, meeting=meeting)

        response = self.client.delete('/voting/attendants/', {'username': user.username, 'meeting': meeting.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(meeting.attendant_set.count(), 0)

class PerfectMeeeting(TestCase):
    @classmethod
    def setUpTestData(self):
        section = 'D-sektionen'
        self.section = create_section(name=section)
        self.users = [create_user([self.section]) for _ in range(5)]
        self.scanners = [create_user([self.section]) for _ in range(2)]
        self.admin, self.admin_client = create_admin([self.section])

    def test_creation(self):

        response = self.admin_client.post('/voting/meetings/', {'name': 'Meeting 1', 'section': str(self.section.id)})
        self.assertEqual(response.status_code, 201)


    def test_perfect_meeting(self):       
        
        admin_create_meeting(self, self.admin_client, self.section.id)

        def admin_add_scanners(self):
            meeting_id = parse(self.admin_client.get('/voting/meetings/'))[0]['id']

            for scanner in self.scanners:
                scanner_res = self.admin_client.post('/voting/scanners/', {'username': scanner[0].username, 'meeting': meeting_id})
                self.assertEqual(scanner_res.status_code, 201)
        admin_add_scanners(self)

        def scanner_add_attendants(self):
            meeting_id = parse(self.scanners[1][1].get('/voting/scanners/'))[0]['meeting']['id']

            for user in self.users:
                attendant_res = self.scanners[1][1].post('/voting/attendants/', {'username': user[0].username, 'meeting': meeting_id})
                self.assertEqual(attendant_res.status_code, 201)
        scanner_add_attendants(self)
			
        # Run vote
        def run_vote(self):

            def admin_create_vote(self):
                meeting_id = parse(self.admin_client.get('/voting/meetings/'))[0]['id']
                alternatives = [{'text': 'D'}, {'text': 'Y'}]

                vote_res = self.admin_client.post('/voting/votes/', {'question': 'Vilken är den bästa sektionen här?', 'meeting': meeting_id, 'alternatives': alternatives}, format='json')
                self.assertEqual(vote_res.status_code, 201)

            admin_create_vote(self)
                         
            # One user votes for Y 
            # The rest votes for the obvious choice: D 
            attendant_votes(self, 0, 1, self.users[0][1])    

            for user in self.users[1:]:
                attendant_votes(self, 0, 0, user[1])
                       
            admin_close_vote(self, 0)

            def admin_count_votes(self):
                vote_id = parse(self.admin_client.get('/voting/votes/'))[0]['id']
                result_res = self.admin_client.get('/voting/votes/'+str(vote_id)+'/')
                self.assertEqual(result_res.status_code, 200)
            
                for result in parse(result_res)['alternatives']:
                    if result['text'] == 'D':
                       self.assertEqual(result['num_votes'], 4) # WOHO WE WON!!!
                    else:
                       self.assertEqual(result['num_votes'], 1)

            admin_count_votes(self)
        run_vote(self)


class BreakBeforeVote(TestCase):
    @classmethod
    def setUpTestData(self):
        section = 'D-sektionen'
        self.section = create_section(name=section)
        self.users = [create_user([self.section]) for _ in range(2)]
        self.scanner, self.scanner_client = create_user([self.section])
        self.admin, self.admin_client = create_admin([self.section])
        
    def test_leave(self):
              
        def admin_actions(self):
            alternatives = [{'text': 'D'}, {'text': 'Y'}]
            meeting_id = parse(self.admin_client.get('/voting/meetings/'))[0]['id']
            vote_res = self.admin_client.post('/voting/votes/', {'question': 'Vilken är den bästa sektionen här?', 'meeting': meeting_id, 'alternatives': alternatives}, format='json')
            
            self.admin_client.post('/voting/attendants/', {'username': self.users[0][0].username, 'meeting': meeting_id})
            attendant_response = self.admin_client.post('/voting/attendants/', {'username': self.users[1][0].username, 'meeting': meeting_id})
            self.assertEqual(attendant_response.status_code, 201)

            user_drop_response = self.admin_client.delete('/voting/attendants/', {'username': self.users[1][0].username, 'meeting': meeting_id})
            self.assertEqual(user_drop_response.status_code, 200)
            self.admin_client.post('/voting/attendants/', {'username': self.users[1][0].username, 'meeting': meeting_id})

        admin_create_meeting(self, self.admin_client, self.section.id)
        admin_actions(self)
        for user in self.users:
            attendant_votes(self, 0, 0, user[1])
        
class BreakAfterVote(TestCase):
    @classmethod
    def setUpTestData(self):
        section = 'D-sektionen'
        self.section = create_section(name=section)
        self.user, self.user_client = create_user([self.section])
        self.scanner, self.scanner_client  = create_user([self.section])
        self.admin, self.admin_client = create_admin([self.section])

    def test_break_after_vote(self):
        
        def admin_actions(self):
            alternatives = [{'text': 'D'}, {'text': 'Y'}]
            meeting_id = parse(self.admin_client.get('/voting/meetings/'))[0]['id']
            self.admin_client.post('/voting/votes/', {'question': 'Vilken är den bästa sektionen här?', 'meeting': meeting_id, 'alternatives': alternatives}, format='json')
            response = self.admin_client.post('/voting/scanners/', {'username': self.scanner.username, 'meeting': meeting_id})
            self.assertEqual(response.status_code, 201)

        def scanner_add_attendants(self):
            meeting_id = parse(self.scanner_client.get('/voting/scanners/'))[0]['meeting']['id']
            self.scanner_client.post('/voting/attendants/', {'username': self.user.username, 'meeting': meeting_id})
        
        def scanner_drop_attendant(self):
            meeting_id = parse(self.scanner_client.get('/voting/scanners/'))[0]['meeting']['id']
            user_drop_response = self.scanner_client.delete('/voting/attendants/', {'username': self.user.username, 'meeting': meeting_id})
            self.assertEqual(user_drop_response.status_code, 200)
        
        def attendant_vote_fail(self):
            vote_obj = parse(self.user_client.get('/voting/votes/?current=true'))[0]
            vote_id = vote_obj['id']
            alternative_id = vote_obj['alternatives'][0]['id']
            uservote_res = self.user_client.post('/voting/made_votes/', {'vote_id': vote_id, 'alternative_id': alternative_id})
            self.assertEqual(uservote_res.status_code, 403)  

        admin_create_meeting(self, self.admin_client, self.section.id)
        admin_actions(self)
        scanner_add_attendants(self)
        attendant_votes(self, 0, 0, self.user_client)
        scanner_drop_attendant(self)
        scanner_add_attendants(self)
        attendant_vote_fail(self)

class ForgotLiUCard(TestCase):
    @classmethod
    def setUpTestData(self):
        section = 'D-sektionen'
        self.section = create_section(name=section)
        self.user, self.user_client = create_user([self.section])
        self.admin, self.admin_client = create_admin([self.section])

    def test_forgot_liu_card(self):
        
        def admin_actions(self):
            meeting_id = parse(self.admin_client.get('/voting/meetings/'))[0]['id']
            self.admin_client.post('/voting/attendants/', {'username': self.user.username, 'meeting': meeting_id})

            alternatives = [{'text': 'D'}, {'text': 'TBI'}]
            self.admin_client.post('/voting/votes/', {'question': 'Vilken är den bästa sektionen här?', 'meeting': meeting_id, 'alternatives': alternatives}, format='json')
        
        def admin_count_votes(self):
            vote_id = parse(self.admin_client.get('/voting/votes/'))[0]['id']
            result_res = self.admin_client.get('/voting/votes/'+str(vote_id)+'/')
            self.assertEqual(result_res.status_code, 200)

            for result in parse(result_res)['alternatives']:
                if result['text'] == 'D':
                    self.assertEqual(result['num_votes'], 1) # WOHO WE WON!!!
                else:
                    self.assertEqual(result['num_votes'], 0)

        admin_create_meeting(self, self.admin_client, self.section.id)
        admin_actions(self)
        attendant_votes(self, 0, 0, self.user_client)
        admin_count_votes(self)   

class WrongSection(TestCase):
    @classmethod
    def setUpTestData(self):
        section = 'D-sektionen'
        self.section = create_section(name=section)
        self.section2 = create_section(name="Test-sektionen")
        self.scanner, self.scanner_client = create_user([self.section2])
        self.user, self.user_client = create_user([self.section])
        self.admin, self.admin_client = create_admin([self.section])

    def test_wrong_section(self):
        # Create meeting
        
        # Make Scanner
        def admin_add_scanners(self):
            meeting_id = parse(self.admin_client.get('/voting/meetings/'))[0]['id']
            scanner_res = self.admin_client.post('/voting/scanners/', {'username': self.scanner.username, 'meeting': meeting_id})
            self.assertEqual(scanner_res.status_code, 201)

        #Scanner adds himself, should fail since scanner is member of the wrong section
        def scanner_add_self(self):
            meeting_id = parse(self.scanner_client.get('/voting/scanners/'))[0]['meeting']['id']
            add_user_fail_response = self.scanner_client.post('/voting/attendants/', {'username': self.scanner.username, 'meeting': meeting_id})
            self.assertEqual(add_user_fail_response.status_code, 400)

            vote_res = parse(self.scanner_client.get('/voting/votes/'))
            self.assertEqual(vote_res, [])    
        
        #def admin_check_attendants(self):
        #    meeting_id = parse(self.admin_client.get('/voting/meetings/'))[0]['id']
        #    attendants_response = self.admin_client.get('/voting/attendants/', {'meeting': meeting_id})
        #    for attendant in parse(attendants_response):
        #       print(attendant)

        admin_create_meeting(self, self.admin_client, self.section.id)
        admin_add_scanners(self)
        scanner_add_self(self)

class PizzaBreak(TestCase):
    @classmethod
    def setUpTestData(self):
        section = 'D-sektionen'
        self.section = create_section(name=section)
        self.scanner, self.scanner_client = create_user([self.section])
        self.users = [create_user([self.section]) for _ in range(50)]
        self.admin, self.admin_client = create_admin([self.section])

    def test_pizza_break(self):
              
        def admin_add_scanners(self):
            meeting_id = parse(self.admin_client.get('/voting/meetings/'))[0]['id']
            scanner_res = self.admin_client.post('/voting/scanners/', {'username': self.scanner.username, 'meeting': meeting_id})
            self.assertEqual(scanner_res.status_code, 201)

        def admin_create_vote(self, question, alternatives):
            meeting_id = parse(self.admin_client.get('/voting/meetings/'))[0]['id']
            self.admin_client.post('/voting/votes/', {'question': question, 'meeting': meeting_id, 'alternatives': alternatives}, format='json')
     
        def scanner_add_attendants(self):
            meeting_id = parse(self.scanner_client.get('/voting/scanners/'))[0]['meeting']['id']
            for user in self.users:
                self.scanner_client.post('/voting/attendants/', {'username': user[0].username, 'meeting': meeting_id})
        
        def attendants_vote(self):
            for user in self.users:    
                attendant_votes(self, 0, 0, user[1])

        # Check result of first vote
        def admin_check_result1(self):
            vote_id = parse(self.admin_client.get('/voting/votes/'))[0]['id']
            result_res = self.admin_client.get('/voting/votes/'+str(vote_id)+'/')
            for result in parse(result_res)['alternatives']:
                if result['text'] == 'D':
                    self.assertEqual(result['num_votes'], 50) # WOHO WE WON!!!
                else:
                    self.assertEqual(result['num_votes'], 0)

        def scanner_remove_all(self):
            meeting_id = parse(self.scanner_client.get('/voting/scanners/'))[0]['meeting']['id']
            for user in self.users:
                self.scanner_client.delete('/voting/attendants/', {'username': user[0].username, 'meeting': meeting_id})
        
        # Add the second half of users to the meeting
        def scanner_add_half(self):
            meeting_id = parse(self.scanner_client.get('/voting/scanners/'))[0]['meeting']['id']
            for user in self.users[25:]:
                self.scanner_client.post('/voting/attendants/', {'username': user[0].username, 'meeting': meeting_id})

        # Second half of users vote
        def attendants_vote_half(self):
            for user in self.users[25:]:    
                attendant_votes(self, 0, 1, user[1])
   
        # Check result of second vote
        def admin_check_result2(self):
            vote_id = parse(self.admin_client.get('/voting/votes/'))[1]['id']
            result_res = self.admin_client.get('/voting/votes/'+str(vote_id)+'/')
            for result in parse(result_res)['alternatives']:
                if result['text'] == 'En IT:are':
                    self.assertEqual(result['num_votes'], 25) # WOHO WE WON!!!
                else:
                    self.assertEqual(result['num_votes'], 0)

        admin_create_meeting(self, self.admin_client, self.section.id)
        admin_add_scanners(self)
        question = 'Vilken är den bästa sektionen här?'
        alternatives = [{'text': 'D'}, {'text': 'Ling'}]
        admin_create_vote(self, question, alternatives)
        scanner_add_attendants(self)
        attendants_vote(self)
        admin_close_vote(self, 0)
        admin_check_result1(self)
        scanner_remove_all(self)
        question = 'En maskinare, en maskinare. Finns det nånting finare? Finns det nånting finare så är det'
        alternatives = [{'text': 'Två maskinare'}, {'text': 'En IT:are'}]
        admin_create_vote(self, question, alternatives)
        scanner_add_half(self)
        attendants_vote_half(self)
        admin_close_vote(self, 0)
        admin_check_result2(self)

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


ADMIN = 'Own admin'
USER = 'Own user'
SCANNER = 'Own scanner'
OLD_SCANNER = 'Old scanner'
ATTENDANT = 'Own attendant'
OTHER_ADMIN = 'Other admin'
OTHER_USER = 'Other user'
OTHER_SCANNER = 'Other scanner'
OTHER_ATTENDANT = 'Other attendant'

LIST = 'GET'
CREATE = 'POST'
SHOW = 'GET'
UPDATE = 'PATCH'
DESTROY = 'DELETE'


class PermissionTests(TestCase):
    def setUp(self):
        self.own_section = create_section('My section')
        self.other_section = create_section('Other section')
        self.users = {
            ADMIN: create_admin([self.own_section]),
            USER: create_user([self.own_section]),
            SCANNER: create_user([self.own_section]),
            OLD_SCANNER: create_user([self.own_section]),
            ATTENDANT: create_user([self.own_section]),
            OTHER_ADMIN: create_admin([self.other_section]),
            OTHER_USER: create_user([self.other_section]),
            OTHER_SCANNER: create_user([self.other_section]),
            OTHER_ATTENDANT: create_user([self.other_section]),
        }

        self.own_meeting = Meeting.objects.create(name='Own meeting', section=self.own_section)
        self.old_meeting = Meeting.objects.create(name='Old meeting', section=self.own_section)
        self.other_meeting = Meeting.objects.create(name='Other meeting', section=self.other_section)

        Scanner.objects.create(meeting=self.own_meeting, user=self.users[SCANNER][0])
        Scanner.objects.create(meeting=self.old_meeting, user=self.users[OLD_SCANNER][0])
        Scanner.objects.create(meeting=self.other_meeting, user=self.users[OTHER_SCANNER][0])

        Attendant.objects.create(meeting=self.own_meeting, user=self.users[ATTENDANT][0])
        Attendant.objects.create(meeting=self.other_meeting, user=self.users[OTHER_ATTENDANT][0])

        self.own_vote = Vote.objects.create(question='When', meeting=self.own_meeting)
        self.own_alternative = Alternative.objects.create(text='Alternative 1', vote=self.own_vote)
        self.made_vote = MadeVote.objects.create(user=create_user([self.own_section])[0], vote=self.own_vote)

        self.issues = []

    def test_meeting_permissions(self):
        self.performTest([ADMIN, OTHER_ADMIN], LIST, '/voting/meetings/', accept_empty=True)
        self.performTest([ADMIN], CREATE, '/voting/meetings/', {'name': 'Name', 'section': self.own_section.id})
        self.performTest([ADMIN], SHOW, '/voting/meetings/%d/' % self.own_meeting.id)
        self.performTest([ADMIN], UPDATE, '/voting/meetings/%d/' % self.own_meeting.id, {'name': 'Test'})
        self.performTest([], DESTROY, '/voting/meetings/%d/' % self.own_meeting.id)

        self.assertNoIssues()

    def test_scanner_permissions(self):
        self.performTest([ADMIN], LIST, '/voting/scanners/?meeting=%d' % self.own_meeting.id)
        self.performTest([ADMIN], CREATE, '/voting/scanners/', {'meeting': self.own_meeting.id, 'username': self.users[USER][0].username})
        self.performTest([], SHOW, '/voting/scanners/%d/' % self.users[SCANNER][0].id)
        self.performTest([], UPDATE, '/voting/scanners/%d/' % self.users[SCANNER][0].id)
        self.performTest([ADMIN], DESTROY, '/voting/scanners/', {'meeting': self.own_meeting.id, 'username': self.users[USER][0].username})

        self.assertNoIssues()

    def test_attendant_permissions(self):
        self.performTest([ADMIN], LIST, '/voting/attendants/?meeting=%d' % self.own_meeting.id)
        self.performTest([ADMIN, SCANNER], CREATE, '/voting/attendants/', {'meeting': self.own_meeting.id, 'username': self.users[USER][0].username})
        self.performTest([], SHOW, '/voting/attendants/%d/' % self.users[ATTENDANT][0].id)
        self.performTest([], UPDATE, '/voting/attendants/%d/' % self.users[ATTENDANT][0].id)
        self.performTest([ADMIN, SCANNER], DESTROY, '/voting/attendants/', {'meeting': self.own_meeting.id, 'username': self.users[ATTENDANT][0].username})

        self.assertNoIssues()

    def test_vote_permissions(self):
        # Note: Listing votes is allowed by all, but VoteTest.test_list
        # ensures that this is limited to the current section.

        self.performTest(self.users.keys(), LIST, '/voting/votes/')
        self.performTest([ADMIN], CREATE, '/voting/votes/', {'meeting': self.own_meeting.id, 'question': 'What?', 'alternatives': [{'text': 'Yes'}, {'text': 'No'}]})
        self.performTest([ADMIN], SHOW, '/voting/votes/%d/' % self.own_vote.id)
        self.performTest([ADMIN], UPDATE, '/voting/votes/%d/' % self.own_vote.id)
        self.performTest([], DESTROY, '/voting/votes/%d/' % self.own_vote.id)

        self.assertNoIssues()

    def test_voting_permissions(self):
        self.performTest([], LIST, '/voting/made_votes/')
        self.performTest([ATTENDANT], CREATE, '/voting/made_votes/', {'vote_id': self.own_vote.id, 'alternative_id': self.own_alternative.id})
        self.performTest([], SHOW, '/voting/made_votes/%d/' % self.made_vote.id)
        self.performTest([], UPDATE, '/voting/made_votes/%d/' % self.made_vote.id)
        self.performTest([], DESTROY, '/voting/made_votes/%d/' % self.made_vote.id)

        self.assertNoIssues()

    def performTest(self, allowed_users, method, path, data=None, accept_empty=False):
        for identifier, (user, client) in self.users.items():
            db_state = self._enter_atomics()
            if data is not None:
                kwargs = {
                    'data': client._encode_data(data, format='json')[0],
                    'content_type': 'application/json'
                }
            else:
                kwargs = {}

            response = client.generic(method, path, **kwargs)
            if identifier in allowed_users:
                self.verifySuccess(response.status_code, response.content, identifier + ' could not execute ' + method + ' on ' + path, accept_empty)
            else:
                self.verifyFailure(response.status_code, response.content, identifier + ' could incorrectly execute ' + method + ' on ' + path, accept_empty)

            #print(response.content)
            self._rollback_atomics(db_state)

    def assertNoIssues(self):
        self.assertEqual(0, len(self.issues), 'One or more issues were found!')

    def verifyFailure(self, status_code, content, msg, accept_empty):
        if status_code not in [403, 404, 405]:
            if accept_empty and content == b'[]':
                return
            else:
                self.issues += [msg]
                print('FOUND ISSUE:', msg)

    def verifySuccess(self, status_code, content, msg, accept_empty):
        if status_code in [403, 404, 405]:
            if accept_empty and content == b'[]':
                return
            else:
                self.issues += [msg]
                print('FOUND ISSUE:', msg)


class WebsocketTest(ChannelTestCase):
    def test_successful(self):
        section = create_section('Section')
        meeting = Meeting.objects.create(name='Meeting 1', section=section)
        user, http_client = create_admin([section])
        token = http_client._credentials['HTTP_AUTHORIZATION'][4:]

        client = WSClient()
        client.send_and_consume('websocket.connect', path='/meeting/%d/?token=%s' % (meeting.id, token))

        # Verify that there is nothing to receive
        self.assertIsNone(client.receive())

        # Test addition of scanners
        scanner = Scanner.objects.create(user=user, meeting=meeting)
        message = client.receive(json=True)
        self.assertEqual('scanner_list', message['type'])
        self.assertEqual(1, len(message['data']))
        self.assertEqual(user.id, message['data'][0]['user']['id'])
        self.assertEqual(user.username, message['data'][0]['user']['username'])

        # Test removal of scanners
        scanner.delete()
        message = client.receive(json=True)
        self.assertEqual('scanner_list', message['type'])
        self.assertEqual(0, len(message['data']))

        # Test addition of attendants
        attendant = Attendant.objects.create(user=user, meeting=meeting)
        message = client.receive(json=True)
        self.assertEqual('attendants_list', message['type'])
        self.assertEqual(1, len(message['data']))
        self.assertEqual(user.id, message['data'][0]['user']['id'])
        self.assertEqual(user.username, message['data'][0]['user']['username'])
        self.assertEqual(meeting.id, message['data'][0]['meeting'])

        # Test voting
        vote = Vote.objects.create(question='Question?', meeting=meeting)
        MadeVote.objects.create(user=user, vote=vote)
        message = client.receive(json=True)
        self.assertEqual('vote_details', message['type'])

        # Test removal of attendants
        attendant.delete()
        message = client.receive(json=True)
        self.assertEqual('attendants_list', message['type'])
        self.assertEqual(0, len(message['data']))

        # Verify that there is nothing to receive
        self.assertIsNone(client.receive())

    def test_unsuccessful(self):
        section = create_section('Section')
        meeting = Meeting.objects.create(name='Meeting 1', section=section)
        user, http_client = create_admin([])
        token = http_client._credentials['HTTP_AUTHORIZATION'][4:]

        client = WSClient()
        with self.assertRaises(AssertionError) as context:
            client.send_and_consume('websocket.connect', path='/meeting/%d/?token=%s' % (meeting.id, token))

        message = context.exception.args[0]
        self.assertTrue('Not permitted' in message)
