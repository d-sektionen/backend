from django.core.management.base import BaseCommand
from ...models import Profile

class Command(BaseCommand):
    help = """
    Fix invalid card id's
    """

    def handle(self, *args, **kwargs):
        for profile in Profile.objects.all():
            if isinstance(profile.liu_card_id, str):
                profile.liu_card_id = None
                profile.save()
