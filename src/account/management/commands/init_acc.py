from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ...tests.factories import UserFactory

class Command(BaseCommand):
    help = "Initialize fake accounts for testing purposes"

    def handle(self, *args, **kwargs):
        try:
            count = int(input("How many users would you like to create? "))
            if count <= 0:
                self.stdout.write(self.style.ERROR("Please enter a positive number."))
                return
        except ValueError:
            self.stdout.write(self.style.ERROR("Invalid input. Please enter a valid number."))
            return

        UserFactory.create_batch(count)
        self.stdout.write(self.style.SUCCESS(f"Successfully created {count} fake users."))
