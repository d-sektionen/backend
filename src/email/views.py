from django.template.loader import render_to_string
from rest_framework.decorators import (
    action,
)
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from post_office import mail

from email.serializers import (
    EmailTemplateSerializer,
    EmailSerializer,
)
from email.models import EmailTemplate
from account.models import EmailSubscription
from datetime import date, datetime
from view_helpers import getEventData
from email.permissions import EmailPermission


class EmailViewSet(viewsets.ViewSet):
    permission_classes = (EmailPermission,)

    @action(detail=False, methods=["get"])
    def templates(self, request):
        try:
            templates = EmailTemplate.objects.all()
            serializer = EmailTemplateSerializer(templates, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except EmailTemplate.DoesNotExist:
            return Response(
                {"error": "No templates found"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=["get"])
    def send_preview(self, request):
        try:
            template = EmailTemplate.objects.get(pk=request.query_params["id"])
            context = self.get_context_data()
            html_code = render_to_string(template.template_file, context).strip()
            return Response(
                {
                    "name": template.name,
                    "category": template.category,
                    "subject": template.subject,
                    "html": html_code,
                },
                status=status.HTTP_200_OK,
            )
        except EmailTemplate.DoesNotExist:
            return Response(
                {"error": "Template not found"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=["post"])
    def send_email(self, request):
        serializer = EmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.save()
            schedule_time = (
                email.sendAt
                if email.sendAt or email.sendAt > datetime.now()
                else datetime.now()
            )
            mail.send(
                subject=email.subject,
                message=email.html,
                from_email="info@d-sektionen.se",
                to=(
                    email.sendTo
                    if email.sendTo
                    else self.get_subscribers_emails(email.category)
                ),
                scheduled_time=schedule_time,
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        context["week_number"] = date.today().isocalendar()[1]
        context["events"] = getEventData()

        return context
