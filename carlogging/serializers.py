from rest_framework import serializers
from .models import LogEntry, LogStart
from booking.models import Booking, Item
from booking.serializers import BookingSerializer
from account.serializers import SimpleUserSerializer
from django.contrib.auth.models import User


class LogStartSerializer(serializers.ModelSerializer):
    booking_liu_id = serializers.CharField(max_length=8, write_only=True)

    class Meta:
        model = LogStart
        fields = (
            'logging_user',
            'booking_user',
            'car_booking',
            'booking_liu_id',
            'kilometers',
            'message',
            'car_cleaned',
            'logging_finished',
            'logging_date'
        )
        read_only_fields = (
            'logging_user', 
            'booking_user',
            'car_booking',
            'logging_finished', 
            'logging_date'
        )

    logging_user = SimpleUserSerializer(read_only=True)
    booking_user = SimpleUserSerializer(read_only=True)
    car_booking = BookingSerializer(read_only=True)


class LogEntrySerializer(serializers.ModelSerializer):
    booking_liu_id = serializers.CharField(max_length=8, write_only=True)

    class Meta:
        model = LogEntry
        fields = (
            'logging_user',
            'booking_user',
            'booking_liu_id',
            'log_start',
            'kilometers',
            'message',
            'car_cleaned',
            'logging_date',
            'car_days',
            'trailer_user',
            'trailer_booking',
            'trailer_days',
            'cost',
            'paid'
        )
        read_only_fields = (
            'logging_user', 
            'booking_user', 
            'log_start', 
            'logging_date',
            'trailer_user',
            'trailer_booking', 
            'cost', 
            'paid'
        )

    logging_user = SimpleUserSerializer(read_only=True)
    booking_user = SimpleUserSerializer(read_only=True)
    log_start = LogStartSerializer(read_only=True)
    trailer_user = SimpleUserSerializer(read_only=True)
    trailer_booking = BookingSerializer(read_only=True)
