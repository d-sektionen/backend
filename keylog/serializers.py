from rest_framework import serializers
from django.contrib.auth.models import User

from account.serializers import SimpleUserSerializer
from checkin.serializers import UserIdentifierField
from .models import Key, LogEntry


class LogEntrySerializer(serializers.ModelSerializer):
    taken_by = SimpleUserSerializer(read_only=True)
    returned_by = SimpleUserSerializer(read_only=True)
    key_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Key.objects.all(), source="key"
    )
    taken_by_id = UserIdentifierField(source="taken_by")
    returned_by_id = UserIdentifierField(source="returned_by",)

    class Meta:
        model = LogEntry
        fields = (
            "id",
            "key_id",
            "taken_by",
            "taken_by_id",
            "taken_at",
            "taken_successfully",
            "returned_by",
            "returned_by_id",
            "returned_at",
            "returned_successfully",
        )
        read_only_fields = ("id", "taken_by", "returned_by")
        # extra_kwargs = {"": }


class KeySerializer(serializers.ModelSerializer):
    status = LogEntrySerializer()

    class Meta:
        model = Key
        fields = ("name", "description", "status", "color", "order")
