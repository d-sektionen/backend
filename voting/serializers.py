from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from account.serializers import SimpleUserSerializer, SectionSerializer
from voting.models import Meeting, Scanner, Attendant, Vote, MadeVote, Section, Alternative


class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ('id', 'name', 'current_vote', 'section', 'archived')


class MeetingReadSerializer(MeetingSerializer):
    section = SectionSerializer()


class ScannerSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer()
    meeting = MeetingSerializer()

    class Meta:
        model = Scanner
        fields = ('id', 'user', 'meeting')


class SimpleScannerSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer()

    class Meta:
        model = Scanner
        fields = ('id', 'user')


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
    has_voted = serializers.SerializerMethodField()

    class Meta:
        model = Vote
        fields = ('id', 'question', 'open', 'alternatives', 'meeting', 'has_voted')

    def get_has_voted(self, obj):
        current_user = self.context['request'].user
        return MadeVote.objects.filter(user=current_user, vote=obj).exists()


class VoteDetailsSerializer(serializers.ModelSerializer):
    alternatives = PrivateAlternativeSerializer(source='alternative_set', many=True)

    class Meta:
        model = Vote
        fields = ('id', 'question', 'open', 'alternatives')


class MadeVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MadeVote
        fields = ('id', 'user', 'vote')
