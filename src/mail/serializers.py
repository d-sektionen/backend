from rest_framework import serializers
from .models import MailTemplate, Mail
from django.template.loader import render_to_string
from datetime import date
from .view_helpers import getEventData
import nh3


class InfomailSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=200, required=True)
    content = serializers.CharField(max_length=4000, required=True)


class MailTemplateSerializer(serializers.ModelSerializer):
    template = serializers.SerializerMethodField()

    def get_context_data(self, **kwargs):
        context = {}

        context["week_number"] = date.today().isocalendar()[1]
        context["events"] = getEventData()

        return context

    def get_template(self, obj):
        context = self.get_context_data()
        html_code = render_to_string(obj.template_filename, context).strip()

        return html_code

    class Meta:
        model = MailTemplate
        fields = ["id", "name", "category", "subject", "description", "template"]


class MailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mail
        fields = ["id", "subject", "html", "category"]


class SendMailSerializer(serializers.ModelSerializer):
    send_at = serializers.DateTimeField(required=False)

    def validate_html(self, value):
        # Sanitize HTML content
        return nh3.clean(value)

    class Meta:
        model = Mail
        fields = ["id", "subject", "html", "category", "send_at"]
