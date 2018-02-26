from datetime import datetime

from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from storage.models import StorageRoom, Location, Booking, Object


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ('group', 'location', 'start_date', 'until_further_notice', 'description')


class ObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Object
        fields = ('name', 'location', 'description', 'in_date', 'out_date', 'amount', 'belongs_to')


class LocationSerializer(serializers.ModelSerializer):
    current_booking = serializers.SerializerMethodField()
    objects = ObjectSerializer(source='object_set', many=True)

    class Meta:
        model = Location
        fields = ('name', 'room', 'can_contain_objects', 'current_booking', 'objects')

    def get_current_booking(self, obj):
        now = datetime.now()
        return obj.booking_set.filter(start_date__lte=now, end_date__gte=now).first()


class StorageRoomSerializer(serializers.ModelSerializer):
    locations = LocationSerializer(source='location_set', many=True)

    class Meta:
        model = StorageRoom
        fields = ('name', 'longitude', 'latitude', 'locations')
