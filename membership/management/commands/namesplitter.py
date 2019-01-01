from django.core.management.base import BaseCommand
import json

class Command(BaseCommand):
    help = """
    Splits names into first and last names.
    If there are more than two parts of the name it will interactively ask what's what.

    The input json should be structured like the following, with appropriate values:
    {
      "anykeyname": [
        ...,
        {
          "name": "Emil Nilsson",
          ...
        },
        ...
      ]
    }

    The output will be the same but include "first_name" and "last_name" instead of name.
    """
    

    def add_arguments(self, parser):
        parser.add_argument('inputfile', type=str, help='The json file for the input.')
        parser.add_argument('outputfile', type=str, help='The json file for the output.')

    def handle(self, *args, **kwargs):
        inputfile = kwargs['inputfile']
        outputfile = kwargs['outputfile']

        data = None
        with open(inputfile) as f:
            data = json.load(f)

        for registration in data:
          print(registration)
          for member in data[registration]:
            split_name = member['name'].split(' ')
            del member['name']
            if len(split_name) == 2:
              member['first_name'] = split_name[0]
              member['last_name'] = split_name[1]
            else:
              print(split_name)
              first_names = int(input('How many are first names? '))

              member['first_name'] = ' '.join(split_name[:first_names])
              member['last_name'] = ' '.join(split_name[first_names:])
              
        with open(outputfile, 'w') as outfile:
            json.dump(data, outfile, ensure_ascii=False, indent=4)