from django.core.management.base import BaseCommand
import re
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = """
    Sets email addresses for users without one if their usernames seem to be liu-id's.
    """

    def handle(self, *args, **kwargs):
        regex = re.compile(r"^[a-z]{4,5}[0-9]{3}$")  # LiU-id regex.
        for user in User.objects.filter(email=""):
            if regex.match(user.username):
                user.email = user.username + "@student.liu.se"
                user.save()
