import json

from django.test import TestCase, Client

from account.tests import AuthenticatedTestCase, create_section, create_admin

class BasicTest(AuthenticatedTestCase):
    def test_creation(self):
        section = create_section('Section')
        admin, client = create_admin([section])

        response = client.post('/voting/meetings/', {'name': 'Meeting 1', 'section': str(section.id)}).json()

        self.assertEqual(response.status_code, 201)

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