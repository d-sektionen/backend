from factory import django, Faker, fuzzy
from ..models import Member

class MemberFactory(django.DjangoModelFactory):
    class Meta:
        model = Member

    liu_id = Faker("lexify", letters="abcdefghijklmnopqrstuvwxyz", text=Faker("numerify", text="?????###"))  # Get a believable LiU ID
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    membership_type = fuzzy.FuzzyChoice(Member.MEMBERSHIP_TYPE_CHOICES, getter=lambda c: c[0])
