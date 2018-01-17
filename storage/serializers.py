from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from storage.models import StorageRoom, Location, Booking, Object

class StorageRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorageRoom
        fields = ('name', 'longitude', 'latitude')

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('name', 'room', 'can_contain_objects')


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ('group', 'location', 'start_date', 'until_further_notice', 'description')

class ObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Object
        fields = ('name', 'location', 'description', 'in_date', 'out_date', 'amount', 'belongs_to')
