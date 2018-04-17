from datetime import datetime

from rest_framework import serializers

from account.models import is_user_in_group
from account.serializers import CommitteeSerializer
from storage.models import StorageRoom, Location, Booking, Object


class BookingSerializer(serializers.ModelSerializer):
    group = CommitteeSerializer()

    class Meta:
        model = Booking
        fields = ('id', 'group', 'location', 'start_date', 'end_date', 'until_further_notice', 'description')


class ObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Object
        fields = ('id', 'name', 'location', 'description', 'in_date', 'amount', 'belongs_to', 'private', 'can_be_borrowed')


class LocationSerializer(serializers.ModelSerializer):
    current_booking = serializers.SerializerMethodField()
    objects = ObjectSerializer(source='object_set', many=True, read_only=True)

    class Meta:
        model = Location
        fields = ('id', 'name', 'room', 'description', 'can_contain_objects', 'current_booking', 'objects')

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        # Censor the objects field if the user doesn't have the sufficient permissions to view them
        if self.context:
            request = self.context.get('request')
            if request:
                if not instance.has_permissions(request.user):
                    ret['objects'] = []

        return ret

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
        fields = ('id', 'name', 'longitude', 'latitude', 'locations', 'description', 'model_url')
