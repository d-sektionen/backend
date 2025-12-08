from django.contrib.auth.models import User
from rest_framework import serializers
from ..account.serializers import SimpleUserSerializer
from datetime import timedelta
from .models import ItemPool, Booking, ItemPoolAccessory, ItemPoolItem


class ItemSerializer(serializers.ModelSerializer):
    image_processed = serializers.ImageField(read_only=True)
    category = serializers.StringRelatedField()

    class Meta:
        model = ItemPool
        fields = ("id", "name", "description", "category", "terms", "image_processed")
        read_only_fields = (
            "id",
            "name",
            "description",
            "category",
            "terms",
            "image_processed",
        )


class ItemPoolItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemPoolItem
        fields = ("id", "name")
        read_only_fields = ("id", "name")


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
    pool = ItemSerializer(read_only=True)
    items = ItemPoolItemSerializer(many=True, read_only=True)
    accessories = AccessorySerializer(many=True, read_only=True)
    count = serializers.IntegerField(write_only=True)

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

        lower_duration = 2 * 24 if restricted_timeslot else 0.5
        upper_duration = 30 * 24 if restricted_timeslot else 3 * 24

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

        # assign items and, if needed, accessories
        items, accessories = self.assign_items_accessories(attrs)

        attrs["items"] = items
        attrs["accessories"] = accessories

        # the model itself does not have a count field:
        # it's only used to assign items and accessories
        del attrs["count"]

        return attrs

    def assign_items_accessories(self, attrs):
        # collect items with available accessories, choosing those with
        # highest priority first
        all_items = (
            ItemPoolItem.objects.filter(pool=attrs["pool"]).order_by("priority").all()
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
                print(f"Item {item} is not available due to overlap.")
                continue

            if attrs["pool"].requires_accessory:
                accessory = (
                    ItemPoolAccessory.objects.filter(pool=attrs["pool"])
                    .filter(compatible_items=item)
                    .first()
                )

                if accessory and accessory not in accessories:
                    accessories.append(accessory)
                    items.append(item)
            else:
                items.append(item)

            if len(items) >= attrs["count"]:
                # we're done!
                break

        if len(items) < attrs["count"]:
            raise serializers.ValidationError(
                "Not enough items or accessories available to satisfy the booking."
            )

        return items, accessories


class DenyBookingSerializer(serializers.ModelSerializer):
    reason = serializers.CharField(max_length=255)

    class Meta:
        model = Booking
        fields = ("id", "reason")
