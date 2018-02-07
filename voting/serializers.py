from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from account.serializers import SimpleUserSerializer
from voting.models import Meeting, Scanner, Attendant, Vote, MadeVote, Section, Alternative


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ('id', 'name',)


class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ('id', 'name', 'current_vote', 'section', 'archived')


class ScannerSerializer(serializers.ModelSerializer):
    meeting = MeetingSerializer()

    class Meta:
        model = Scanner
        fields = ('id', 'user', 'meeting')


class AttendantSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer()

    class Meta:
        model = Attendant
        fields = ('id', 'user', 'meeting')


class PublicAlternativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alternative
        fields = ('id', 'text',)


class PrivateAlternativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alternative
        fields = ('id', 'text', 'num_votes')


class VoteListSerializer(WritableNestedModelSerializer):
    alternatives = PublicAlternativeSerializer(source='alternative_set', many=True)

    class Meta:
        model = Vote
        fields = ('id', 'question', 'open', 'alternatives', 'meeting')


class VoteDetailsSerializer(serializers.ModelSerializer):
    alternatives = PrivateAlternativeSerializer(source='alternative_set', many=True)

    class Meta:
        model = Vote
        fields = ('id', 'question', 'open', 'alternatives')


class MadeVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MadeVote
        fields = ('id', 'user', 'vote')
