from datetime import datetime

from rest_framework import serializers

from storage.models import StorageRoom, Location, Booking, Object


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ('id', 'group', 'location', 'start_date', 'end_date', 'until_further_notice', 'description')


class ObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Object
        fields = ('id', 'name', 'location', 'description', 'in_date', 'out_date', 'amount', 'belongs_to')


class LocationSerializer(serializers.ModelSerializer):
    current_booking = serializers.SerializerMethodField()
    objects = ObjectSerializer(source='object_set', many=True, read_only=True)

    class Meta:
        model = Location
        fields = ('id', 'name', 'room', 'can_contain_objects', 'current_booking', 'objects')

    def get_current_booking(self, obj):
        now = datetime.now()
        booking = obj.booking_set.filter(start_date__lte=now, end_date__gte=now).first()
        if booking is not None:
            return BookingSerializer(booking).data
        else:
            return None


class StorageRoomSerializer(serializers.ModelSerializer):
    locations = LocationSerializer(source='location_set', many=True, read_only=True)

    class Meta:
        model = StorageRoom
        fields = ('id', 'name', 'longitude', 'latitude', 'locations')
