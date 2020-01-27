from rest_framework import serializers
from .models import Logg

class LoggSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logg
        fields = ("start_km", "end_km", "user", "cost", "trailer", "trailer_days", "car_days", "active_member")
        read_only_fields = ("cost")
    
    cost = serializers.Field(source="calc_cost")

    def validate(self, attrs):
        if attrs["start_km"] > attrs["end_km"]:
            raise serializers.ValidationError("Start kilometer should be less than end kilometer")
        if attrs['trailer_days'] < 0:
            raise serializers.ValidationError("Days trailer is rented can't be less than 0!")
