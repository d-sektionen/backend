from django.contrib.auth.models import User
from rest_framework import serializers
from ..account.serializers import SimpleUserSerializer
from datetime import timedelta
from .models import Item, Booking


class ItemSerializer(serializers.ModelSerializer):
    image_processed = serializers.ImageField(read_only=True)
    category = serializers.StringRelatedField()

    class Meta:
        model = Item
        fields = (
            "id",
            "name",
            "description",
            "category",
            "terms",
            "image_processed",
            "max_booking_hours",
            "max_booking_hours_restricted_timeslot",
        )
        read_only_fields = (
            "id",
            "name",
            "description",
            "category",
            "terms",
            "image_processed",
            "max_booking_hours",
            "max_booking_hours_restricted_timeslot",
        )


class BookingSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=User.objects.all(),
        source="user",
        default=serializers.CurrentUserDefault(),
    )
    item_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Item.objects.all(), source="item"
    )
    item = ItemSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = (
            "id",
            "start",
            "end",
            "user",
            "user_id",
            "item_id",
            "item",
            "description",
            "confirmed",
            "restricted_timeslot",  # Booking can be changed type by anyone, but will still be validated.
        )
        read_only_fields = ("confirmed",)

    def validate_user_id(self, value):
        user = self.context["request"].user

        if (not user.has_perm("booking.add_booking")) and user.id != value.id:
            raise serializers.ValidationError(
                "You are only allowed to book for yourself."
            )
        return value

    def validate(self, attrs):
        restricted_timeslot = attrs["restricted_timeslot"]

        lower_duration = 2 * 24 if restricted_timeslot else 0.5
        upper_duration = (
            attrs["item"].max_booking_hours_restricted_timeslot
            if restricted_timeslot
            else attrs["item"].max_booking_hours
        )

        lower_timedelta = timedelta(hours=lower_duration)
        upper_timedelta = timedelta(hours=upper_duration)

        # Start should be before end
        if attrs["start"] > attrs["end"]:
            raise serializers.ValidationError("Booking should start before it ends.")
        # Check lowest duration
        if attrs["start"] + lower_timedelta > attrs["end"]:
            raise serializers.ValidationError(
                f"Booking should have a duration of at least {str(lower_timedelta)}."
            )
        # Check longest duration
        if attrs["start"] + upper_timedelta < attrs["end"]:
            raise serializers.ValidationError(
                f"Booking should have a duration of at most {str(upper_timedelta)}."
            )

        # Check overlap
        overlap_query = Booking.objects.filter(
            item=attrs["item"], restricted_timeslot=restricted_timeslot
        )
        if self.instance:
            overlap_query = overlap_query.exclude(pk=self.instance.id)
        overlap_query = overlap_query.filter(
            start__lte=attrs["end"], end__gte=attrs["start"]
        )
        if overlap_query.exists():
            raise serializers.ValidationError("Booking overlaps with another booking.")
        return attrs


class DenyBookingSerializer(serializers.ModelSerializer):
    reason = serializers.CharField(max_length=255)

    class Meta:
        model = Booking
        fields = ("id", "reason")
