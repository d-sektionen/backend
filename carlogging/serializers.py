from rest_framework import serializers
from .models import LogEntry, LogStart
from booking.models import Booking, Item
from account.serializers import SimpleUserSerializer
from django.contrib.auth.models import User


class LogStartSerializer(serializers.ModelSerializer):
    booking_liu_id = serializers.CharField(max_length=8, write_only=True)

    class Meta:
        model = LogStart
        fields = (
            "start_km",
            "start_message",
            "logging_user",
            "booking_user",
            "booking_liu_id",
            "start_car_cleaned",    
            "logging_finished",
            "logging_date",
        )
        read_only_fields = ("logging_user", "logging_finished", "logging_date", "booking_user")

    logging_user = SimpleUserSerializer(read_only=True)
    booking_user = SimpleUserSerializer(read_only=True)


class LogEntrySerializer(serializers.ModelSerializer):
    booking_liu_id = serializers.CharField(max_length=8, write_only=True)

    class Meta:
        model = LogEntry
        fields = (
            "log_start",
            "end_km",
            "end_message",
            "end_car_cleaned",
            "logging_user",
            "booking_user",
            "booking_liu_id",
            "cost",
            "trailer",
            "trailer_days",
            "car_days",
            "logging_date",
            "paid",
        )
        read_only_fields = ("cost", "logging_user", "log_start", "logging_date", "booking_user", "paid")

    logging_user = SimpleUserSerializer(read_only=True)
    booking_user = SimpleUserSerializer(read_only=True)
    log_start = LogStartSerializer(read_only=True)
