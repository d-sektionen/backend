from django.contrib.auth.models import User
from rest_framework import serializers

from .utils import assign_items_and_accessories, should_auto_confirm
from ..account.serializers import SimpleUserSerializer
from datetime import timedelta
from .models import ItemPool, Booking, ItemPoolAccessory, ItemPoolItem


class ItemPoolSerializer(serializers.ModelSerializer):
    image_processed = serializers.ImageField(read_only=True)
    category = serializers.StringRelatedField()
    items = serializers.SerializerMethodField()
    accessories = serializers.SerializerMethodField()

    def get_items(self, obj):
        return ItemPoolItemSerializer(
            ItemPoolItem.objects.filter(pool=obj, enabled=True), many=True
        ).data

    def get_accessories(self, obj):
        return AccessorySerializer(
            ItemPoolAccessory.objects.filter(pool=obj), many=True
        ).data

    class Meta:
        model = ItemPool
        fields = (
            "id",
            "name",
            "description",
            "category",
            "terms",
            "image_processed",
            "max_booking_hours",
            "max_booking_hours_restricted_timeslot",
            "requires_accessory",
            "items",
            "accessories",
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
            "requires_accessory",
            "items",
            "accessories",
        )


class ItemPoolItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemPoolItem
        fields = ("id", "name", "status")
        read_only_fields = ("id", "name", "status")


class AccessorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemPoolAccessory
        fields = ("id", "name")
        read_only_fields = ("id", "name")


class BookingSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=User.objects.all(),
        source="user",
        default=serializers.CurrentUserDefault(),
    )
    pool_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=ItemPool.objects.all(), source="pool"
    )
    pool = ItemPoolSerializer(read_only=True)
    items = ItemPoolItemSerializer(many=True, read_only=True)
    accessories = AccessorySerializer(many=True, read_only=True)
    count = serializers.IntegerField()

    class Meta:
        model = Booking
        fields = (
            "id",
            "start",
            "end",
            "user",
            "user_id",
            "pool_id",
            "description",
            "confirmed",
            "accessories",
            "pool",
            "items",
            "count",
            "restricted_timeslot",  # Booking can be changed type by anyone, but will still be validated.
        )
        read_only_fields = ("confirmed", "items", "accessories")

    def validate_user_id(self, value):
        user = self.context["request"].user

        if (not user.has_perm("booking.add_booking")) and user.id != value.id:
            raise serializers.ValidationError(
                "You are only allowed to book for yourself."
            )
        return value

    def validate(self, attrs):
        # remove any smaller time units than a minute to prevent overlap issues with
        # continous bookings that start and end at the same time
        attrs["start"] = attrs["start"].replace(second=0, microsecond=0)
        attrs["end"] = attrs["end"].replace(second=0, microsecond=0)

        restricted_timeslot = attrs["restricted_timeslot"]

        # there is no reason to book with restricted timeslot if you are booking
        # shorter than the maximum time allowed for normal bookings
        lower_duration = attrs["pool"].max_booking_hours if restricted_timeslot else 0.5
        upper_duration = (
            attrs["pool"].max_booking_hours_restricted_timeslot
            if restricted_timeslot
            else attrs["pool"].max_booking_hours
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

        if attrs["count"] <= 0:
            raise serializers.ValidationError("Booking count must be at least 1.")

        items, accessories = assign_items_and_accessories(
            self.instance,
            attrs["start"],
            attrs["end"],
            attrs["pool"],
            attrs["count"],
            attrs["restricted_timeslot"],
        )

        if should_auto_confirm(attrs, self.instance):
            # automatically assign items and, if needed, accessories
            attrs["items"] = items
            attrs["accessories"] = accessories
        else:
            # werk will assign the items and accessories manually upon confirmation
            # we still run assign_items_and_accessories to error out if there are not enough items or accessories available
            pass

        return attrs


class ConfirmBookingSerializer(serializers.ModelSerializer):
    items = serializers.ListField(child=serializers.IntegerField(), required=False)
    accessories = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )
    auto_assign = serializers.BooleanField(default=False)

    class Meta:
        model = Booking
        fields = ("id", "items", "accessories", "auto_assign")


class DenyBookingSerializer(serializers.ModelSerializer):
    reason = serializers.CharField(max_length=255)

    class Meta:
        model = Booking
        fields = ("id", "reason")
