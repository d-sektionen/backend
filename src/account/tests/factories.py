from factory import RelatedFactory, Trait, django, Faker, LazyAttribute
from account.models import Profile, User
from django.db.models.signals import post_save
from faker import Faker as RealFaker

RealFaker = RealFaker()

class ProfileFactory(django.DjangoModelFactory):
    class Meta:
        model = Profile

    liu_card_id = Faker("random_number", digits=17, fix_len=True)
    infomail_subscriber = True


@django.mute_signals(post_save)
class UserFactory(django.DjangoModelFactory):
    """
    Creates a batch of users in the system according the LiU ID system ABCXY123 base on first and last name and some random numbers
    """
    class Meta:
        model = User

    first_name = Faker("first_name")
    last_name = Faker("last_name")
    username = LazyAttribute(
        lambda obj: obj.first_name[:3].lower() + obj.last_name[:2].lower() + RealFaker.numerify(text="###")
    )
    email = LazyAttribute(lambda obj: obj.username+"@student.liu.se")
    # Not one to one with how the model is laid out, but works for testing
    profile = RelatedFactory(
        ProfileFactory,
        factory_related_name="user",
    )

    # TODO: post generation password
    class Params:
        # We might want to give the admin user all perms? https://gist.github.com/bee-keeper/9857973
        admin = Trait(
            is_superuser=True,
            is_staff=True,
        )
