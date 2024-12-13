from django.template.loader import get_template, render_to_string
from rest_framework.decorators import (
    action,
)
from rest_framework import viewsets
from rest_framework.response import Response
from account.permissions import AllowMembers
from rest_framework import status
from post_office import mail

from email.serializers import InfomailSerializer, EmailTemplateSerializer, EmailSerializer
from email.models import EmailTemplate
from account.models import Profile, EmailSubscription
from datetime import date, datetime
from view_helpers import getEventData

# render_infomail_template() will be removed
def render_infomail_template(subject_context, content_context):
    subject_template = get_template("email/infomail.subject.txt")
    content_template = get_template("email/infomail.html")

    subject_html = subject_template.render(subject_context).strip()
    content_html = content_template.render(content_context).strip()

    return subject_html, content_html

# InfoMailViewSet will be removed
class InfoMailViewSet(viewsets.ViewSet):
    # TODO: Add proper perms
    permission_classes = (AllowMembers,)

    def list(self, request):
        return Response({})

    @action(detail=False, methods=["post"])
    def send(self, request):
        serializer = InfomailSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        profiles = Profile.objects.filter(infomail_subscriber=True)
        emails = [i.user.email for i in profiles]

        subject_html, content_html = render_infomail_template(
            {"subject": serializer.validated_data["subject"]},
            {"content": serializer.validated_data["content"]},
        )

        mail.send(
            recipients=["info@d-sektionen.se"],
            bcc=emails,
            message=content_html,
            subject=subject_html,
        )

        return Response(status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"])
    def send_sample(self, request):
        serializer = InfomailSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        subject_html, content_html = render_infomail_template(
            {"subject": serializer.validated_data["subject"]},
            {"content": serializer.validated_data["content"]},
        )

        mail.send(
            recipients=["info@d-sektionen.se"],
            message=content_html,
            subject=subject_html,
        )

        return Response(status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"])
    def preview(self, request):
        serializer = InfomailSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        subject_html, content_html = render_infomail_template(
            {"subject": serializer.validated_data["subject"]},
            {"content": serializer.validated_data["content"]},
        )

        return Response(
            {"subject": subject_html, "content": content_html},
        )

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        context["week_number"] = date.today().isocalendar()[1]
        context["events"] = getEventData()

        return context

class EmailViewSet(viewsets.ViewSet):
    permission_classes = (AllowMembers,)

    @action(detail=False, methods=["get"])
    def templates(self, request):
        try:
            templates = EmailTemplate.objects.all()
            serializer = EmailTemplateSerializer(templates, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except EmailTemplate.DoesNotExist:
            return Response({"error": "No templates found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["get"])
    def preview(self, request):
        try:
            template = EmailTemplate.objects.get(pk=request.query_params["id"])
            context = self.get_context_data()
            html_code = render_to_string(template.template_file, context).strip()
            return Response({"name": template.name,
                            "category": template.category,
                            "subject": template.subject,
                            "html": html_code}, status=status.HTTP_200_OK)
        except EmailTemplate.DoesNotExist:
            return Response({"error": "Template not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["post"])
    def emails(self, request):
        serializer = EmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.save()
            schedule_time = email.sendAt if email.sendAt or email.sendAt > datetime.now() else datetime.now()
            mail.send(
                subject=email.subject,
                message=email.html,
                from_email='info@d-sektionen.se',
                to= self.get_subscribers_emails(email.category), # NOTE: Unsure on the category functionality
                scheduled_time=schedule_time,
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        context["week_number"] = date.today().isocalendar()[1]
        context["events"] = getEventData()

        return context

    def get_subscribers_emails(self, category):
        email_subscribers = EmailSubscription.objects.filter(category=category)
        return [i.user.email for i in email_subscribers]