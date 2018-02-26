from django.core.management.base import BaseCommand

from account.models import Section
from storage.models import StorageRoom, Location


class Command(BaseCommand):
    help = 'Provides dummy data to make testing on a fresh database easier.'

    def handle(self, *args, **options):
        a15 = StorageRoom()
        a15.name = 'A15'
        a15.latitude = '58.40224'
        a15.longitude = '15.577426'
        #a15.description = 'A15 är ett förråd. Här kan du lagra vad du vill som sektionsaktiv. Här är lite mer info om A15 och dess användningsområden.'
        a15.save()

        hylla1 = Location()
        hylla1.name = 'Hylla 1'
        hylla1.can_contain_objects = True
        hylla1.room = a15
        hylla1.save()


