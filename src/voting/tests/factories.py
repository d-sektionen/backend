from factory import RelatedFactory, django, Faker, SubFactory
from ..models import Alternative, Attendant, MadeVote, Meeting, Vote
from ...account.tests.factories import UserFactory


class VoteFactory(django.DjangoModelFactory):
    class Meta:
        model = Vote

    question = Faker("sentence", nb_words=4)
    meeting = SubFactory("voting.tests.MeetingFactory")


class AlternativeFactory(django.DjangoModelFactory):
    class Meta:
        model = Alternative

    text = Faker("sentence", nb_words=2)
    num_votes = 0
    vote = SubFactory(VoteFactory)


class MeetingFactory(django.DjangoModelFactory):
    """Sets up a meeting with:"""

    class Meta:
        model = Meeting

    name = Faker("sentence", nb_words=2)
    description = Faker("sentence", nb_words=4)
    clear_data = Faker("date_this_year", after_today=False)

    current_vote = RelatedFactory(
        VoteFactory,
        factory_related_name="meeting",
    )


class AttendantFactory(django.DjangoModelFactory):
    class Meta:
        model = Attendant

    user = SubFactory(UserFactory)
    meeting = SubFactory(MeetingFactory)


class MadeVoteFactory(django.DjangoModelFactory):
    class Meta:
        model = MadeVote

    user = SubFactory(UserFactory)
    vote = SubFactory(VoteFactory)
