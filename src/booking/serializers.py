from .models import Item, Booking
from django.contrib.auth.models import User
from rest_framework import serializers
from account.serializers import SimpleUserSerializer
from datetime import datetime, timedelta


class ItemSerializer(serializers.ModelSerializer):
    image_processed = serializers.ImageField(read_only=True)
    category = serializers.StringRelatedField()

    class Meta:
        model = Item
        fields = ("id", "name", "description", "category", "terms", "image_processed")
        read_only_fields = (
            "id",
            "name",
            "description",
            "category",
            "terms",
            "image_processed",
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

        self.check_overlap(attrs, restricted_timeslot)

        return attrs

    def check_overlap(self, attrs, restricted_timeslot):
        # Find all bookings that overlap any part of this booking
        overlap_query = Booking.objects.filter(
            item=attrs["item"], restricted_timeslot=restricted_timeslot
        )
        if self.instance:
            overlap_query = overlap_query.exclude(pk=self.instance.id)
        overlap_query = overlap_query.filter(
            start__lte=attrs["end"], end__gte=attrs["start"]
        )

        # Sort the start and end times for each booking
        events: list[tuple[datetime, int]] = []
        for other in overlap_query:
            clamped_start = max(attrs["start"], other.start)
            events.append((clamped_start, other.count))

            clamped_end = min(attrs["end"], other.end)
            events.append((clamped_end, -other.count))

        events.sort(key=lambda item: item[0])  # sort by time

        # Step through `events` and record whenever count exceeds the available count of this object
        count = attrs.get("count") or 1
        limit = attrs["item"].count
        exceeded_periods: list[tuple[datetime, datetime]] = []
        exceeded_from = None

        for time, delta in events:
            count += delta

            print(f"{time} {delta=} {count=}")

            if count > limit:
                if not exceeded_from:
                    # we just exceeded the limit
                    exceeded_from = time
            elif exceeded_from:
                # we no longer exceed the limit, store the offending period and conitnue
                exceeded_periods.append((exceeded_from, time))
                exceeded_from = None

        if len(exceeded_periods) > 0:

            def format_date(datetime):
                return datetime.strftime("%Y-%m-%d %H:%M")

            message = ", ".join(
                [
                    f"{format_date(start)} to {format_date(end)}"
                    for start, end in exceeded_periods
                ]
            )

            raise serializers.ValidationError(
                f"Item count is exceeded during {message}"
            )


class DenyBookingSerializer(serializers.ModelSerializer):
    reason = serializers.CharField(max_length=255)

    class Meta:
        model = Booking
        fields = ("id", "reason")
