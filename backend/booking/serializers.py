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

        # assign items and accessories, if needed
        count = attrs["count"]
        all_items = (
            ItemPoolItem.objects.filter(pool=attrs["pool"]).order_by("priority").all()
        )

        items = []
        accessories = []

        for item in all_items:
            accessory = (
                ItemPoolAccessory.objects.filter(pool=attrs["pool"])
                .filter(compatible_items=item)
                .first()
            )

            if accessory and accessory not in accessories:
                accessories.append(accessory)
                items.append(item)

            if len(items) >= count:
                break

        if len(items) < count:
            raise serializers.ValidationError(
                "Not enough items or accessories available to satisfy the booking."
            )

        attrs["items"] = items
        attrs["accessories"] = accessories

        print(attrs)

        # TODO: check overlap

        # the model itself does not have a count field:
        # it's only used to assign items and accessories
        del attrs["count"]

        return attrs


class DenyBookingSerializer(serializers.ModelSerializer):
    reason = serializers.CharField(max_length=255)

    class Meta:
        model = Booking
        fields = ("id", "reason")
