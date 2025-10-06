from datetime import date, timedelta
from django.core.management.base import BaseCommand
from account.models import Profile
from committee.models import CommitteeMember
from committee.models import Committee
import json 
import os
import csv
import re

class Command(BaseCommand):
    help = "updating active users"
    def handle (self, *args, **kwargs):
            
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


