from django.core.management.base import BaseCommand
from account.models import Profile
from committee.models import CommitteeMember
from committee.models import Committee
import json 
import os

class Command(BaseCommand):
    help = "Updating active users"

    def handle(self, *args, **kwargs):
        directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'committee_members')
        filename = 'committee_collection.json'
        file_path = os.path.join(directory, filename)

        with open(file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            for person in data:
                print(person["Förnamn"], person["Efternamn"], person["E-post"], person["Utskott"], person["Post"])
                
        #for person in CommitteeMember.objects.all():
            #try:
                #person.profile.is_active = True
                # if person.profile.user.username == "luklu706":
                #     person.role_type = "tr"
                #     person.role_name = "Kassör"
                    
                #     committee_id = Committee.objects.get(name="WebbU")
                #     #Check if utskott exists else add it or print it
                #     print(committee_id.id)

                #     person.save()
                # person.save()
            # except Exception:
            #     self.stdout.write(f"Can't find user {person.profile}")
            #     continue # Continue to try and find next user
            
