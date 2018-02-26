from django.core.management.base import BaseCommand

from account.models import Section


class Command(BaseCommand):
    help = 'Provides dummy data to make testing on a fresh database easier.'

    def handle(self, *args, **options):
        section = Section()
        section.name = 'D-sektionen'
        section.program_codes = '6CDDD 6CMJU 6CITE 6KIPR 6KCCC 6MDAV'
        section.save()
