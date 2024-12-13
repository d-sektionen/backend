from rest_framework import serializers
from .models import EmailTemplate, Email


class InfomailSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=200, required=True)
    content = serializers.CharField(max_length=4000, required=True)

class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = ['id', 'name', 'category', 'subject', 'description']

class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Email
        fields = ['id', 'subject', 'html', 'sendAt', 'category']