from rest_framework import serializers
from ..account.serializers import SimpleUserSerializer
from .models import Occurrence


class OccurrenceSerializer(serializers.ModelSerializer):
    attendants = SimpleUserSerializer(read_only=True, many=True)

    class Meta:
        model = Occurrence
        depth = 2
        fields = (
            "id",
            "name",
            "archived",
            "clear_data",
            "attendants",
            "attendant_limit",
            "members_only",
            "whitelist",
            "blacklist",
        )

    def validate_attendant_limit(self, value):
        if value < 0:
            raise serializers.ValidationError("Attendant limit must be a positive value.")
        return value
