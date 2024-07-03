from factory import RelatedFactory, Trait, django, Faker
from account.models import Profile, User
from django.db.models.signals import post_save


class ProfileFactory(django.DjangoModelFactory):
    class Meta:
        model = Profile

    liu_card_id = Faker("random_number", digits=17, fix_len=True)


@django.mute_signals(post_save)
class UserFactory(django.DjangoModelFactory):
    class Meta:
        model = User

    username = Faker("lexify", letters="abcdefghijklmnopqrstuvwxyz", text=Faker("numerify", text="?????###"))  # Get a believable LiU ID
    RelatedFactory(
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
