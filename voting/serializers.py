from rest_framework import serializers

from voting.models import Meeting, Scanner, Attendant, Vote, MadeVote, Section


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ('name',)


class MeetingSerializer(serializers.ModelSerializer):
    section = SectionSerializer()

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


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ('question', 'open', 'meeting')


class MadeVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MadeVote
        fields = ('user', 'vote')
