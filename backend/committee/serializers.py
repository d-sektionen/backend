from django.contrib.auth.models import Permission
from rest_framework import serializers

from ..committee.models import Committee, CommitteeMember


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = (
            "codename",
            "id",
        )


class CommitteeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Committee
        fields = ("name", "id")


class CommitteeMemberWithoutProfileSerializer(serializers.ModelSerializer):
    """Avoid recursion when serializing CommitteeMembers in ProfileSerializer."""

    committee = CommitteeSerializer()

    class Meta:
        model = CommitteeMember
        fields = (
            "email",
            "role_name",
            "role_type",
            "year",
            "committee",
            "has_permissions_until",
        )


class CommitteeMemberSerializer(CommitteeMemberWithoutProfileSerializer):
    class Meta:  # type: ignore[assignment]
        model = CommitteeMember
        fields = (
            "email",
            "role_name",
            "role_type",
            "year",
            "committee",
            "has_permissions_until",
            "profile",
        )
