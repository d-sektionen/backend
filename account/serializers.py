from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import serializers

from membership.utils import check_membership
from checkin.models import Doorkeeper

from .models import Profile, CalendarSubscription
from . import user


class CommitteeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ("id", "name")


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("liu_card_id", "infomail_subscriber")


class UserSerializer(serializers.ModelSerializer):
    committees = serializers.SerializerMethodField()
    membership = serializers.SerializerMethodField()
    pretty_name = serializers.SerializerMethodField()
    privileges = serializers.SerializerMethodField()
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "pretty_name",
            "committees",
            "membership",
            "profile",
            "privileges",
        )

    def get_membership(self, obj):
        return check_membership(obj.username)

    def get_pretty_name(self, obj):
        return obj.get_full_name() if obj.get_full_name() else obj.get_username()

    def get_committees(self, obj):
        # TODO: fix this
        committees = Group.objects.filter(id__in=obj.groups.all())
        return CommitteeSerializer(committees, many=True).data

    def get_privileges(self, obj):
        return {
            "booking_admin": obj.has_perms(
                (
                    "booking.add_booking",
                    "booking.change_booking",
                    "booking.delete_booking",
                    "booking.view_booking",
                )
            ),
            "doorkeeper": Doorkeeper.objects.filter(user=obj).exists(),
            "attendance_admin": obj.has_perms(
                (
                    "attendance.add_occurrence",
                    "attendance.change_occurrence",
                    "attendance.delete_occurrence",
                    "attendance.view_occurrence",
                )
            ),
            "voting_admin": obj.has_perms(
                (
                    "voting.add_meeting",
                    "voting.change_meeting",
                    "voting.delete_meeting",
                    "voting.view_meeting",
                )
            ),
            "member": check_membership(obj.username),
            "staff": obj.is_staff,
        }

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile")
        # Unless the application properly enforces that this field is
        # always set, the follow could raise a `DoesNotExist`, which
        # would need to be handled.
        profile = ""
        if hasattr(instance, "profile"):
            profile = instance.profile
        else:
            profile = Profile()

        # instance.username = validated_data.get('username', instance.username) # Username should never be updated
        instance.email = validated_data.get("email", instance.email)
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.save()

        profile.liu_card_id = profile_data.get("liu_card_id", profile.liu_card_id)
        profile.infomail_subscriber = profile_data.get(
            "infomail_subscriber", profile.infomail_subscriber
        )

        profile.save()

        return instance

    def create(self, validated_data):
        profile_data = validated_data.pop("profile")
        user = User.objects.create(**validated_data)
        Profile.objects.create(user=user, **profile_data)
        return user


class SimpleUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "pretty_name")
        read_only_fields = ("id", "username", "first_name", "last_name", "pretty_name")


class InfomailUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "pretty_name")
        read_only_fields = ("id", "username", "email", "pretty_name")


class CalendarSubscriptionSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return self.context["request"].build_absolute_uri(
            reverse("calendar_feed", kwargs={"pk": obj.id})
        )

    class Meta:
        model = CalendarSubscription
        fields = (
            "id",
            "url",
            "user",
            "include_bookings",
            "include_events_attending",
            "include_events_not_attending",
        )
        read_only_fields = ("id", "user", "url")
