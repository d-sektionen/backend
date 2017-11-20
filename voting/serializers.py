from rest_framework import serializers

from voting.models import Meeting, Scanner, Attendant, Vote, MadeVote, Section, Alternative


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ('name',)


class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ('name', 'current_vote', 'section', 'archived')


class ScannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scanner
        fields = ('user', 'meeting')


class AttendantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendant
        fields = ('user', 'meeting')


class PublicAlternativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alternative
        fields = ('text',)


class PrivateAlternativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alternative
        fields = ('text', 'num_votes')


class VoteListSerializer(serializers.ModelSerializer):
    alternatives = PublicAlternativeSerializer(source='alternative_set', many=True)

    class Meta:
        model = Vote
        fields = ('question', 'open', 'alternatives')


class VoteDetailsSerializer(serializers.ModelSerializer):
    alternatives = PrivateAlternativeSerializer(source='alternative_set', many=True)

    class Meta:
        model = Vote
        fields = ('question', 'open', 'alternatives')


class MadeVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MadeVote
        fields = ('user', 'vote')
