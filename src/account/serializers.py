from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import serializers

from membership.utils import check_membership
from checkin.models import Doorkeeper

from .models import Profile, CalendarSubscription


class PublicProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)

    class Meta:
        model = Profile
        fields = ("first_name", "last_name")


class PrivateProfileSerializer(PublicProfileSerializer):
    def update(self, instance, validated_data):
        # WARN: first_name and last_name is updated by ADFS on each request.
        instance.liu_card_id = validated_data.get("liu_card_id", instance.liu_card_id)
        instance.infomail_subscriber = validated_data.get(
            "infomail_subscriber", instance.infomail_subscriber
        )
        instance.save()

        return instance

    class Meta:
        model = Profile
        fields = (
            "first_name",
            "last_name",
            "liu_card_id",
            "infomail_subscriber",
        )


class MeSerializer(serializers.ModelSerializer):
    membership = serializers.SerializerMethodField()
    pretty_name = serializers.SerializerMethodField()
    privileges = serializers.SerializerMethodField()
    profile = PrivateProfileSerializer()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "pretty_name",
            "membership",
            "profile",
            "privileges",
        )

    def get_membership(self, obj):
        return check_membership(obj.username)

    def get_pretty_name(self, obj):
        return obj.get_full_name() if obj.get_full_name() else obj.get_username()

    def get_privileges(self, obj):
        profile = Profile.objects.get(user=obj)

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
            "voting_counter": obj.has_perms(("voting.view_meeting",)),
            "not_member": not check_membership(obj.username),
            "member": check_membership(obj.username),
            "staff": obj.is_staff,
            "committee_active": profile.has_active_committee_membership(),
        }


class SimpleUserSerializer(MeSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "pretty_name")
        read_only_fields = ("id", "username", "first_name", "last_name", "pretty_name")


class InfomailUserSerializer(MeSerializer):
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
            "include_bookings_by_user",
            "include_bookable_items",
        )
        read_only_fields = ("id", "user", "url")
