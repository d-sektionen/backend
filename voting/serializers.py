from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers
from django.contrib.auth.models import User

from membership.utils import check_membership
from account.serializers import SimpleUserSerializer

from .models import Meeting, Attendant, Vote, MadeVote, Alternative, SpeakerRequest


class MeetingAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = (
            "id",
            "name",
            "current_vote",
            "clear_data",
            "archived",
            "open_attendance",
            "enable_speaker_requests",
        )
        read_only_fields = ("current_vote",)


class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ("id", "name", "open_attendance", "enable_speaker_requests")
        read_only_fields = ("id", "name", "open_attendance", "enable_speaker_requests")


class AttendantSerializer(serializers.ModelSerializer):
    user_username = serializers.SlugRelatedField(
        slug_field="username",
        write_only=True,
        queryset=User.objects.all(),
        source="user",
    )
    user = SimpleUserSerializer(read_only=True)
    meeting_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Meeting.objects.all(), source="meeting"
    )
    meeting = MeetingAdminSerializer(read_only=True)

    def validate_user_username(self, value):
        """
        Validate that user is a member.
        """
        user = User.objects.get(username=value)
        if not check_membership(user.get_username()):
            raise serializers.ValidationError("User is not a member")
        return value

    class Meta:
        model = Attendant
        fields = ("id", "user", "meeting", "user_username", "meeting_id")


class PublicAlternativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alternative
        fields = ("id", "text")


class PrivateAlternativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alternative
        fields = ("id", "text", "num_votes")


class VoteListSerializer(WritableNestedModelSerializer):
    alternatives = PublicAlternativeSerializer(source="alternative_set", many=True)
    has_voted = serializers.SerializerMethodField()

    class Meta:
        model = Vote
        fields = ("id", "question", "open", "alternatives", "meeting", "has_voted")

    def get_has_voted(self, obj):
        current_user = self.context["request"].user
        return MadeVote.objects.filter(user=current_user, vote=obj).exists()


class VoteDetailsSerializer(serializers.ModelSerializer):
    alternatives = PrivateAlternativeSerializer(source="alternative_set", many=True)

    class Meta:
        model = Vote
        fields = ("id", "question", "open", "alternatives")


class MadeVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MadeVote
        fields = ("id", "user", "vote")


class SpeakerRequestSerializer(serializers.ModelSerializer):
    meeting_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Meeting.objects.all(), source="meeting"
    )
    user = SimpleUserSerializer(read_only=True)

    class Meta:
        model = SpeakerRequest
        fields = ("id", "user", "meeting_id")
