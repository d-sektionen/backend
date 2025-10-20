from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from account.models import Profile
from committee.models import CommitteeMember
from committee.models import Committee
from datetime import datetime
import random
import json 
import os
import csv
import re

class Command(BaseCommand):
    help = "updating active users"
    def handle (self, *args, **kwargs):
        run_import = False
        run_committee = False
        run_fake_committee = False
        try:
            import_response = input("Would you like to run the import script?")
            if import_response == "yes" or import_response == "y":
                run_import = True
            committee_response = input("Would you like to run the create committees script?")
            if committee_response == "yes" or committee_response == "y":
                run_committee = True
            fake_committee = input("Would you like to run the fake committee import script?")
            if fake_committee == "yes" or fake_committee == "y":
                run_fake_committee = True
        except ValueError:
            self.stdout.write(self.style.ERROR("Not a valid response, exiting"))
            return
        
        if(run_import and run_committee):
            import_committee()
            create_committees()
        elif(run_import):
            import_committee()
        elif(run_committee):
            create_committees()
        elif(run_fake_committee):
            import_fake_committee()
        else:
            return



def import_committee():
        def get_liu_email(liuid):
            return liuid + "@student.liu.se"

        def get_utskott(filename):
            match = re.search(r'-\s*(.*?)\.', filename)
            result = match.group(1)
            return result

        def get_permission_date():
            #1a Juli året efter
            today = date.today()
            one_year_later = date.today() + timedelta(days=365) 
            return str(one_year_later)

        def get_post_description(post):
            chairman_names = ["Ordförande", "Chief", "Lagkapten", "Gamemaster", "Projektledare", "Bandledare", "Infochef", "General", "Programledare", "Webmaster", "Intendent"]
            treasurer_names = ["Ca$h", "Kassör", ]
            if(post in chairman_names):
                return "Ordförande"
            elif (post in treasurer_names):
                return "Kassör"
            else:
                return "Utskottsmedlem"


        # Output file name

        # Files to skip
        skip_files = {
            'Integrering - Sammanställning.csv',
            'Integrering - Översikt.csv',
            'collection.py',
            'committee_collection.json'
        }

        # Create list to store all rows
        all_rows = []
        directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'committee_members')
        output_path = os.path.join(directory, 'committee_collection.json')
        csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]

        # Loop through files in current directory
        for filename in csv_files:
            if filename in skip_files or not filename.endswith('.csv'):
                continue
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row['Förnamn'].strip() == '' and row['Efternamn'].strip() == '':
                        continue

                    #Add Utskott field accordning to filename
                    row["Utskott"] = get_utskott(filename)
                    
                    #Add liu email
                    row["E-post"] = get_liu_email(row['LiU-id'])

                    #Add end date when permissions should no longer be active  
                    row["Permissions_until"] = get_permission_date()

                    #Add post description
                    row["Post_description"] = get_post_description(row["Post"])

                    all_rows.append(row)
                    

        #Write all collected rows to one JSON array
        with open(output_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(all_rows, jsonfile, ensure_ascii=False, indent=4)

def create_committees():
        directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'committee_members')
        filename = 'committee_collection_test.json'
        file_path = os.path.join(directory, filename)

        with open(file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            for person in data:
                try:
                    #Check if the Committee exists
                    _committee = Committee.objects.get(name=person["Utskott"])
                except Committee.DoesNotExist:
                    #If not, create it
                    print(f"Committee with name {person['Utskott']} does not exist. Creating new committee.")
                    _committee = Committee.objects.create(name=person["Utskott"])
                
                try:   
                    _profile = Profile.objects.get(user__username=person["LiU-id"])
                except Profile.DoesNotExist:
                    print(f"Profile with LiU-id {person['LiU-id']} does not exist. Skipping.")
                    continue

                try:   
                    _permissions_until = datetime.strptime(person["Permissions_until"], "%Y-%m-%d")                
                except Profile.DoesNotExist:
                    print(f"Profile with permission date {person['Permissions_until']} does not have a valid date. Skipping.")
                    continue

                #Check if the CommitteeMember already exists
                committee_member, created = CommitteeMember.objects.get_or_create(
                    profile = _profile,
                    committee = _committee,
                    has_permissions_until = _permissions_until,
                )

                # if not created:
                #     # Update existing CommitteeMember
                #     committee_member.role_name = person["Post"]
                #     committee_member.role_type = person["Post_description"]
                #     committee_member.permissions_until = person["Permissions_until"]
                #     committee_member.save()

def import_fake_committee():
        def get_liu_email(liuid):
            return liuid + "@student.liu.se"

        def get_utskott(filename):
            match = re.search(r'-\s*(.*?)\.', filename)
            result = match.group(1)
            return result

        def get_permission_date():
            #1a Juli året efter
            today = date.today()
            one_year_later = date.today() + timedelta(days=365) 
            return str(one_year_later)

        def get_post_description(post):
            chairman_names = ["Ordförande", "Chief", "Lagkapten", "Gamemaster", "Projektledare", "Bandledare", "Infochef", "General", "Programledare", "Webmaster", "Intendent"]
            treasurer_names = ["Ca$h", "Kassör", ]
            if(post in chairman_names):
                return "Ordförande"
            elif (post in treasurer_names):
                return "Kassör"
            else:
                return "Utskottsmedlem"


        # Create list to store all rows
        rows = []
        directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'committee_members')
        output_path = os.path.join(directory, 'committee_collection_test.json')

        # Loop through files in current directory
        for profile in Profile.objects.all():
            row = {
                "Förnamn": profile.user.first_name,  # you can split this out of the username or leave blank
                "Efternamn": profile.user.last_name,   # you can split this out of the username or leave blank
                "LiU-id": profile.user.username,
                "Post": "",
                "B23-tillträde": "false",
                "Utskott": "",
                "E-post": profile.user.email or f"{profile.user.username}@student.liu.se",
                "Permissions_until": timezone.now().date().strftime("%Y-%m-%d"),
                "Post_description": "",
            }
            rows.append(row)

        output_path = os.path.join(directory, 'committee_collection.json')
        
        with open(output_path, 'r', encoding='utf-8') as jsonfile:
            print("Reading existing committee collection")
            existing_rows = json.load(jsonfile)
            for index, n_row in enumerate(existing_rows):
                if index < len(rows):
                    rows[index]["Post"] = n_row["Post"]
                    rows[index]["Utskott"] = n_row["Utskott"]
                    rows[index]["Post_description"] = n_row["Post_description"]
                    rows[index]["Permissions_until"] = n_row["Permissions_until"]
        print(rows)
                
        output_path = os.path.join(directory, 'committee_collection_test.json')

        #Write all collected rows to one JSON array
        with open(output_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(rows, jsonfile, ensure_ascii=False, indent=4)