from django.template.loader import get_template
from rest_framework.decorators import (
    action,
)
from rest_framework import viewsets
from rest_framework.response import Response
from account.permissions import AllowMembers
from rest_framework import status
from post_office import mail

from infomail.serializers import InfomailSerializer
from account.models import Profile
from datetime import date
from view_helpers import getEventData

def render_infomail_template(subject_context, content_context):
    subject_template = get_template("email/infomail.subject.txt")
    content_template = get_template("email/infomail.html")

    subject_html = subject_template.render(subject_context).strip()
    content_html = content_template.render(content_context).strip()

    return subject_html, content_html


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
