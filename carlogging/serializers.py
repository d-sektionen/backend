from rest_framework import serializers
from .models import Logg
from account.serializers import SimpleUserSerializer
from django.contrib.auth.models import User

class LoggSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logg
        fields = ("start_km", "end_km", "user", "cost", "trailer", "trailer_days", "car_days", "active_member")
        read_only_fields = ("cost", "user")
    
    cost = serializers.SerializerMethodField()
    #user = SimpleUserSerializer(read_only=True)
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )
    def get_cost(self, obj):
        return obj.calc_cost()

    def validate(self, attrs):
        if attrs['start_km'] == None:
            attrs['start_km'] = 0
        if attrs['end_km'] == None:
            attrs['end_km'] = 0
        if attrs["start_km"] > attrs["end_km"]:
            raise serializers.ValidationError("Start kilometer should be less than end kilometer")
        if attrs['trailer_days'] == None:
            attrs['trailer_days'] = 0
        if attrs['car_days'] == None:
            attrs['car_days'] = 0
        if attrs['trailer_days'] < 0:
            raise serializers.ValidationError("Days trailer is rented can't be less than 0!")
        if attrs['car_days'] < 0:
            raise serializers.ValidationError("Days car is rented can't be less than 0!")
        

        return attrs