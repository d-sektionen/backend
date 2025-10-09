from django.core.management.base import BaseCommand
from ....checkin.models import EventBase
import datetime

class Command(BaseCommand):
    help = 'Commands that should run every night'

    def handle(self, *args, **options):

        """
        Deletes all events where the clear_data date has passed
        """
        events = EventBase.objects.all()
        d = datetime.date.today()
        for event in events:
            if event.clear_data < d:
                event.delete()
