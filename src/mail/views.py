from django.template.loader import render_to_string
from rest_framework.decorators import (
    action,
)
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import StaticHTMLRenderer
from post_office import mail

from .serializers import (
    MailTemplateSerializer,
    MailSerializer,
)
from .models import MailTemplate, Mail
from account.models import EmailSubscription
from datetime import date
from .view_helpers import getEventData
from .permissions import EmailPermission


class MailTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (EmailPermission,)
    queryset = MailTemplate.objects.all()
    serializer_class = MailTemplateSerializer

    @action(detail=True, methods=["get"], renderer_classes=[StaticHTMLRenderer])
    def get_html(self, request, pk=None):
        template = MailTemplate.objects.get(pk=pk)
        context = self.get_context_data()
        html_code = render_to_string(template.template_file.name, context).strip()

        return Response(html_code, status=status.HTTP_200_OK)

    def get_context_data(self, **kwargs):
        context = {}

        context["week_number"] = date.today().isocalendar()[1]
        context["events"] = getEventData()

        return context


class MailViewSet(viewsets.ViewSet):
    permission_classes = (EmailPermission,)
    # TODO: Perm check for specific category?

    @action(detail=False, methods=["post"])
    def send(self, request):
        serializer = MailSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        bcc = self.get_subscribers_emails(serializer.validated_data["category"])

        # TODO: Handle sent at a later date
        email = mail.send(
            recipients=[request.user.email],
            bcc=bcc,
            message=serializer.validated_data["html"],
            subject=serializer.validated_data["subject"],
        )

        Mail.objects.create(
            subject=serializer.validated_data["subject"],
            category=serializer.validated_data["category"],
            post_office_mail=email,
        )

        return Response(status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"])
    def send_sample(self, request):
        serializer = MailSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        mail.send(
            recipients=[request.user.email],
            message=serializer.validated_data["html"],
            subject=serializer.validated_data["subject"],
        )

        return Response(status=status.HTTP_201_CREATED)

    def get_subscribers_emails(self, category):
        # Note: Basic implementation, not very flexible.
        if category == "infomail":
            email_subscribers = EmailSubscription.objects.filter(include_infomail=True)
        elif category == "announcement":
            email_subscribers = EmailSubscription.objects.filter(
                include_announcement=True
            )
        else:
            email_subscribers = EmailSubscription.objects.none()
        return [i.user.email for i in email_subscribers]
