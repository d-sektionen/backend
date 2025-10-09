from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Make existing users staff and super user (takes usernames as a parameters)"

    def add_arguments(self, parser):
        # Creates a list with one or more users supplied from command line.
        parser.add_argument('username', nargs='+', type=str)

    def handle(self, *args, **kwargs):
        for name in kwargs['username']:
            try:
                user = User.objects.get(username=name)
            except Exception:
                self.stdout.write(f"Can't find user {name}")
                continue # Continue to try and find next user

            # Make user admin
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(f"User {name} is now admin")
