from django.contrib.auth.models import User
from rest_framework import serializers

from .utils import should_auto_confirm
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
            ItemPoolItem.objects.filter(pool=obj), many=True
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

        if should_auto_confirm(attrs, self.instance):
            # automatically assign items and, if needed, accessories
            items, accessories = self.assign_items_accessories(attrs)

            attrs["items"] = items
            attrs["accessories"] = accessories
        else:
            # werk will assign the items and accessories manually upon confirmation
            pass

        return attrs

    def assign_items_accessories(self, attrs):
        # collect items with available accessories, choosing those with
        # highest priority first
        all_items = (
            ItemPoolItem.objects.filter(pool=attrs["pool"], enabled=True)
            .order_by("-priority")
            .all()
        )

        overlap_query = Booking.objects.filter(
            pool=attrs["pool"], restricted_timeslot=attrs["restricted_timeslot"]
        )
        if self.instance:
            overlap_query = overlap_query.exclude(pk=self.instance.id)
        overlap_query = overlap_query.filter(
            start__lte=attrs["end"], end__gte=attrs["start"]
        )

        items = []
        accessories = []

        for item in all_items:
            item_overlap_query = overlap_query.filter(items__in=[item])

            if item_overlap_query.exists():
                continue

            if attrs["pool"].requires_accessory:
                compat_accessories = (
                    ItemPoolAccessory.objects.filter(pool=attrs["pool"])
                    .filter(compatible_items=item)
                    .all()
                )

                # find the first accessory (if any) that is not already assigned
                for accessory in compat_accessories:
                    if accessory in accessories:
                        continue  # already assigned for this booking

                    # check overlap for accessory as well
                    accessory_overlap_query = overlap_query.filter(
                        accessories__in=[accessory]
                    )
                    if accessory_overlap_query.exists():
                        continue  # accessory is already booked in overlapping period
                    accessories.append(accessory)
                    items.append(item)
                    break
            else:
                items.append(item)

            if len(items) >= attrs["count"]:
                # we're done!
                break

        if len(items) < attrs["count"]:
            raise serializers.ValidationError(
                "Not enough available items or accessories available to satisfy the booking."
            )

        return items, accessories


class ConfirmBookingSerializer(serializers.ModelSerializer):
    items = serializers.ListField(child=serializers.IntegerField())
    accessories = serializers.ListField(child=serializers.IntegerField())

    class Meta:
        model = Booking
        fields = ("id", "items", "accessories")


class DenyBookingSerializer(serializers.ModelSerializer):
    reason = serializers.CharField(max_length=255)

    class Meta:
        model = Booking
        fields = ("id", "reason")
