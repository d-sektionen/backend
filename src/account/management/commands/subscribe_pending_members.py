from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from membership.models import Request


class Command(BaseCommand):
    help = """
    Subscribes all users with pending membership requests to the infomail.
    """

    def handle(self, *args, **kwargs):
        for request in Request.objects.all():
            user = User.objects.get(username=request.username)
            user.profile.infomail_subscriber = True
            user.save()

