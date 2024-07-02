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
            "description",
            "current_vote",
            "clear_data",
            "archived",
            "open_attendance",
            "enable_speaker_requests",
        )
        read_only_fields = ("current_vote",)


class MeetingSerializer(serializers.ModelSerializer):

    attending = serializers.SerializerMethodField()

    def get_attending(self, obj):
        current_user = self.context["request"].user
        return Attendant.objects.filter(user=current_user, meeting=obj).exists()

    class Meta:
        model = Meeting
        fields = (
            "id",
            "name",
            "description",
            "attending",
            "open_attendance",
            "enable_speaker_requests",
        )
        read_only_fields = (
            "id",
            "name",
            "description",
            "attending",
            "open_attendance",
            "enable_speaker_requests",
        )


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
    has_voting_rights = serializers.BooleanField(required=True)

    def validate_user_username(self, value):
        """
        Validate that user and voting_rights are an allowed combination
        """
        user = User.objects.get(username=value)
        is_member = check_membership(user.get_username())
        requested_voting_rights = self.initial_data.get("has_voting_rights")
        
        if not is_member and requested_voting_rights == True:
            raise serializers.ValidationError(
                "User is not a member and voting rights were requested to be set to True"
            )
        elif is_member and requested_voting_rights == False:
            raise serializers.ValidationError(
                "User is a member and voting rights were requested to be set to False"
            )
        elif not isinstance(requested_voting_rights, bool):
            raise serializers.ValidationError("Invalid data")

        return value

    class Meta:
        model = Attendant
        fields = ("id", "user", "meeting", "user_username", "meeting_id", 
                  "has_voting_rights")


class SelfAttendSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)
    meeting_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Meeting.objects.all(), source="meeting"
    )
    meeting = MeetingSerializer(read_only=True)

    def validate_meeting_id(self, value):
        if value.open_attendance:
            return value
        raise serializers.ValidationError("Meeting is not open")

    class Meta:
        model = Attendant
        fields = ("id", "user", "meeting", "meeting_id")


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

    def validate_meeting_id(self, value):
        if not value.enable_speaker_requests:
            raise serializers.ValidationError(
                "Speaker requests are disabled for this meeting."
            )
        current_user = self.context["request"].user
        if not Attendant.objects.filter(user=current_user, meeting=value).exists():
            raise serializers.ValidationError("You are not attending this meeting.")

        return value

    class Meta:
        model = SpeakerRequest
        fields = ("id", "user", "meeting_id", "prioritized")
