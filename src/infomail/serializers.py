from rest_framework import serializers


class InfomailSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=200, required=True)
    content = serializers.CharField(max_length=4000, required=True)
