from rest_framework import serializers
from .models import LogEntry, LogStart
from booking.models import Booking, Item
from account.serializers import SimpleUserSerializer
from django.contrib.auth.models import User


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
