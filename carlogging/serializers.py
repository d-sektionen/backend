from rest_framework import serializers
from .models import LogEntry, LogStart
from booking.models import Booking, Item
from account.serializers import SimpleUserSerializer
from django.contrib.auth.models import User
from .utils import check_valid_booking


class LogEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LogEntry
        fields = (
            "start_km",
            "start_message",
            "start_car_cleaned",
            "end_km",
            "end_message",
            "end_car_cleaned",
            "user",
            "booking_liu_id",
            "cost",
            "trailer",
            "trailer_days",
            "car_days",
            "active_member",
        )
        read_only_fields = ("cost", "user", "start_km",
                            "start_message", "start_car_cleaned")

    user = SimpleUserSerializer(read_only=True)

    # user = serializers.HiddenField(
    #    default=serializers.CurrentUserDefault(),
    # )

    def create(self, validated_data, **kwargs):
        validated_data["user"] = self.context["request"].user

        check_valid_booking(validated_data)

        booking_liu_id = validated_data["booking_liu_id"]
        log_start_exists = LogStart.objects.filter(
            booking_liu_id=booking_liu_id).exists()
        if not log_start_exists:
            raise serializers.ValidationError(
                "No LogStart object has been created for this booking"
            )

        log_start = LogStart.objects.get(booking_liu_id=booking_liu_id)
        if log_start.start_km > validated_data["end_km"]:
            raise serializers.ValidationError(
                # kommer detta kunna ge någon valid http-response till frontenden ???
                "Start kilometer should be less than end kilometer"
            )

        log_entry = LogEntry.objects.create(**validated_data)
        log_entry.cost = log_entry.calc_cost()
        log_entry.start_km = log_start.start_km
        log_entry.start_message = log_start.start_message
        log_entry.start_car_cleaned = log_start.start_car_cleaned
        log_start.delete()  # delete LogStart object so that a new one can be created

        # kanske spara the User som skapade LogStart, i denna LogEntry?

        return log_entry

    def validate(self, attrs):
        if attrs["trailer_days"] == None:
            attrs["trailer_days"] = 0
        if attrs["car_days"] == None:
            attrs["car_days"] = 0
        if attrs["trailer_days"] < 0:
            raise serializers.ValidationError(
                "Days trailer is rented can't be less than 0!"
            )
        if attrs["car_days"] < 0:
            raise serializers.ValidationError(
                "Days car is rented can't be less than 0!"
            )

        return attrs


class LogStartSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogStart
        fields = (
            "start_km",
            "start_message",
            "user",
            "booking_liu_id",
            "start_car_cleaned",
        )
        read_only_fields = ("user",)

    user = SimpleUserSerializer(read_only=True)

    def create(self, validated_data, **kwargs):
        validated_data["user"] = self.context["request"].user

        check_valid_booking(validated_data)

        booking_liu_id = validated_data["booking_liu_id"]
        if LogStart.objects.filter(booking_liu_id=booking_liu_id).exists():
            raise serializers.ValidationError(
                "A LogStart object has already been created for this user"  # ändra lösning???
            )

        log_start = LogStart.objects.create(**validated_data)
        return log_start
