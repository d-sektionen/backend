from django.core.management.base import BaseCommand
import json

from account.user import get_or_create_user


class Command(BaseCommand):
    help = """
    Imports infomail subscribers from a json file.

    The json should be structured like the following, with appropriate values:
    [
      {"email": "emini757@student.liu.se"},
      {"email": "liuid420@student.liu.se"}
    ]
    
    If email is not a @student.liu.se email it will be ignored.
    """

    def add_arguments(self, parser):
        parser.add_argument("inputfile", type=str, help="The json file for the input.")

    def handle(self, *args, **kwargs):
        inputfile = kwargs["inputfile"]

        data = None
        with open(inputfile) as f:
            data = json.load(f)

        for subscriber in data:
            if "@student.liu.se" in subscriber["email"]:
                user, created = get_or_create_user(
                    subscriber["email"].replace("@student.liu.se", "")
                )
                user.profile.infomail_subscriber = True
                user.save()

