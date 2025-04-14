from rest_framework import serializers
from .models import MailTemplate, Mail


class InfomailSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=200, required=True)
    content = serializers.CharField(max_length=4000, required=True)


class MailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MailTemplate
        fields = ["id", "name", "category", "subject", "description"]


class MailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mail
        fields = ["id", "subject", "html", "sendAt", "category", "sendTo"]
