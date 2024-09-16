from rest_framework import serializers
from django.contrib.auth.models import User

from committee.models import Committee


class CommitteeUserSerializer(serializers.ModelSerializer):
    pretty_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = "id", "username", "email", "pretty_name"

    def get_pretty_name(self, obj):
        full_name = obj.get_full_name()
        return full_name if full_name else obj.username


class CommitteeSerializer(serializers.ModelSerializer):
    treasurer = CommitteeUserSerializer()
    chair = CommitteeUserSerializer()
    members = CommitteeUserSerializer(many=True)

    class Meta:
        model = Committee
        fields = (
            "id",
            "name",
            "description",
            "treasurer",
            "treasurer_email",
            "chair",
            "chair_email",
            "members",
        )

