from rest_framework import serializers

from account.serializers import SimpleUserSerializer
from booking.serializers import BookingSerializer
from carlogging.models import LogEntry, LogStart
from committee.serializers import CommitteeSerializer


class LogStartSerializer(serializers.ModelSerializer):
    logging_user = SimpleUserSerializer(read_only=True)
    car_user = SimpleUserSerializer(read_only=True)
    car_booking = BookingSerializer(read_only=True)
    is_finished = serializers.SerializerMethodField()

    class Meta:
        model = LogStart
        fields = ('id',
                  'logging_user',
                  'car_user',
                  'car_booking',
                  'kilometers',
                  'message',
                  'car_cleaned',
                  'is_finished',
                  'logging_date')
        read_only_fields = ('logging_user',
                            'car_user',
                            'car_booking',
                            'logging_date')

    def get_is_finished(self, obj):
        return hasattr(obj, 'log_entry') and obj.log_entry is not None


class LogEntrySerializer(serializers.ModelSerializer):
    logging_user = SimpleUserSerializer(read_only=True)
    car_user = SimpleUserSerializer(read_only=True)
    trailer_user = SimpleUserSerializer(read_only=True)
    trailer_booking = BookingSerializer(read_only=True)
    log_start = LogStartSerializer(read_only=True)
    committee = CommitteeSerializer(read_only=True)

    class Meta:
        model = LogEntry
        fields = ('id',
                  'logging_user',
                  'car_user',
                  'trailer_user',
                  'trailer_booking',
                  'log_start',
                  'committee',
                  'car_days',
                  'trailer_days',
                  'cost',
                  'is_paid',
                  'kilometers',
                  'message',
                  'car_cleaned',
                  'logging_date')
        read_only_fields = ('logging_user',
                            'car_user',
                            'trailer_user',
                            'trailer_booking',
                            'log_start',
                            'cost',
                            'is_paid',
                            'logging_date')
