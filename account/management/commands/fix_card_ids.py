from django.core.management.base import BaseCommand
from account.models import Profile


class Command(BaseCommand):
    help = """
    Fix invalid card id's
    """

    def handle(self, *args, **kwargs):
        for profile in Profile.objects.all():
            if type(profile.liu_card_id) == str:
                profile.liu_card_id = None
                profile.save()

