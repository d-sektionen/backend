from rest_framework import serializers
from .models import LogEntry, LogStart
from booking.models import Booking, Item
from account.serializers import SimpleUserSerializer
from django.contrib.auth.models import User
from .utils import check_valid_booking


class LogStartSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogStart
        fields = (
            "start_km",
            "start_message",
            "logging_user",
            "booking_liu_id",
            "start_car_cleaned",
            "logging_finished",
            "logging_date",
        )
        read_only_fields = ("logging_user", "logging_finished", "logging_date")

    logging_user = SimpleUserSerializer(read_only=True)

    def create(self, validated_data, **kwargs):
        validated_data["logging_user"] = self.context["request"].user
        validated_data["logging_finished"] = False

        check_valid_booking(validated_data)

        booking_liu_id = validated_data["booking_liu_id"]
        if LogStart.objects.filter(
            booking_liu_id=booking_liu_id,
            logging_finished=False
        ).exists():
            raise serializers.ValidationError(
                "A LogStart object has already been created for this user"  # ändra lösning???
            )

        log_start = LogStart.objects.create(**validated_data)

        return log_start


class LogEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LogEntry
        fields = (
            "log_start",
            "end_km",
            "end_message",
            "end_car_cleaned",
            "logging_user",
            "booking_liu_id",
            "cost",
            "trailer",
            "trailer_days",
            "car_days",
            "active_member",
            "logging_date",
        )
        read_only_fields = ("cost", "logging_user", "log_start", "logging_date")

    logging_user = SimpleUserSerializer(read_only=True)
    log_start = LogStartSerializer(read_only=True)

    # user = serializers.HiddenField(
    #    default=serializers.CurrentUserDefault(),
    # )

    def create(self, validated_data, **kwargs):
        validated_data["logging_user"] = self.context["request"].user

        check_valid_booking(validated_data)

        booking_liu_id = validated_data["booking_liu_id"]
        
        log_start_exists = LogStart.objects.filter(
            booking_liu_id=booking_liu_id,
            logging_finished=False
        ).exists()
        if not log_start_exists:
            raise serializers.ValidationError(
                "No LogStart object has been created for this booking"
            )

        log_start = LogStart.objects.get(
            booking_liu_id=booking_liu_id, 
            logging_finished=False
        )
        if log_start.start_km > validated_data["end_km"]:
            raise serializers.ValidationError(
                # kommer detta kunna ge någon valid http-response till frontenden ???
                "Start kilometer should be less than end kilometer"
            )

        validated_data["log_start"] = log_start
        log_entry = LogEntry.objects.create(**validated_data)
        log_entry.cost = log_entry.calc_cost()
        log_entry.save()

        log_start.logging_finished = True
        log_start.save()

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
