from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from membership.models import Request


class Command(BaseCommand):
    help = "Make an existing user a super user (takes the username as a parameter)"

    def add_arguments(self, parser):
        parser.add_argument('username', nargs='+', type=str)

    def handle(self, *args, **kwargs):
        for name in kwargs['username']:
            try:
                user = User.objects.get(username=name)
            except Exception:
                self.stdout.write(f"Can't find user {name}")
        user.is_staff = True
        user.is_superuser = True
        user.save()
        self.stdout.write(f"User {name} is now admin")

