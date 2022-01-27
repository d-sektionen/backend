from dataclasses import field
from rest_framework import serializers
from django.contrib.auth.models import User

from committee.models import Committee


class CommitteeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Committee
        fields = 'id', 'name'