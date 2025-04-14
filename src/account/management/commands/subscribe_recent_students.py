from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = "Subscribes all students from the last N years to the infomail."

    def add_arguments(self, parser):
        parser.add_argument(
            "years",
            type=int,
            help="Number of years to look back for subscribing students to infomail",
        )

    def handle(self, *args, **kwargs):
        years = kwargs["years"]
        time_threshold = timezone.now() - timedelta(days=years * 365)
        recent_users = User.objects.filter(date_joined__gte=time_threshold)

        for user in recent_users:
            user.profile.infomail_subscriber = True
            user.profile.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully subscribed {recent_users.count()} users to infomail."
            )
        )
