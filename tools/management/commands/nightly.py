from django.core.management.base import BaseCommand, CommandError
from checkin.models import Event
import datetime

class Command(BaseCommand):
    help = 'Commands that should run every night'
    
    def handle(self, *args, **options):

        """
        Deletes all events where the clear_data date has passed
        """
        events = Event.objects.all()
        d = datetime.date.today()
        for event in events:
            if event.clear_data < d:
                event.delete()
