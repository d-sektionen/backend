from django.core.management.base import BaseCommand
import json

from membership.models import Member, ProgramRegistration

class Command(BaseCommand):
    help = """
    Imports users from a json file.

    The json should be structured like the following, with appropriate values:
    {
      "6cmju-3-ht2018": [
        ...,
        {
          "first_name": "Emil",
          "last_name": "Nilsson",
          "liu_id": "emini757"
        },
        ...
      ]
    }
    """

    def add_arguments(self, parser):
        parser.add_argument('inputfile', type=str, help='The json file for the input.')

    def handle(self, *args, **kwargs):
        inputfile = kwargs['inputfile']

        data = None
        with open(inputfile) as f:
            data = json.load(f)

        for program in data:
          for member in data[program]:
            obj, created = Member.objects.get_or_create(
              liu_id=member['liu_id'],
              defaults={
                'first_name': member['first_name'],
                'last_name': member['last_name']
              }
            )
            ProgramRegistration.objects.get_or_create(member=obj, registration=program)
