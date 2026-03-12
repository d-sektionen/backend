from rest_framework import views
from rest_framework.response import Response
from django.http import HttpResponse

from backend.mail.permissions import SenderPermission

from .view_helpers import generate_mail_context
from ..app.utils import render_email
from post_office import mail

from ..account.models import Profile


class PreviewView(views.APIView):
    def post(self, request):
        content = request.data.get("content", "")
        info_chief_content = request.data.get("infoChiefContent", "")
        context = generate_mail_context(content, info_chief_content)

        _subject, content = render_email("email/newsletter", context)
        return HttpResponse(content, content_type="text/html")


class SendView(views.APIView):
    permission_classes = [SenderPermission]

    def post(self, request):
        subject = request.data.get("subject", "Infomail")
        content = request.data.get("content", "")
        info_chief_content = request.data.get("infoChiefContent", "")
        context = generate_mail_context(
            content, info_chief_content, subject=subject, force_fetch=True
        )

        subject, content = render_email("email/newsletter", context)

        mail_recipients: list[str] = list(
            Profile.objects.filter(infomail_subscriber=True).values_list(
                "user__email", flat=True
            )
        )

        mail.send(
            recipients=[],  # hide recipients email adresses
            bcc=mail_recipients,  # blind carbon copy all recipients
            subject=subject,
            html_message=content,
            priority="now",  # High priority
        )

        return Response({"status": "sent"})


class SendSelfView(views.APIView):
    permission_classes = [SenderPermission]

    def post(self, request):
        subject = request.data.get("subject", "Infomail")
        content = request.data.get("content", "")
        info_chief_content = request.data.get("infoChiefContent", "")
        context = generate_mail_context(
            content, info_chief_content, subject=subject, force_fetch=True
        )

        subject, content = render_email("email/newsletter", context)

        mail_recipients = [request.user.email]

        mail.send(
            recipients=[],  # hide recipients email adresses
            bcc=mail_recipients,  # blind carbon copy all recipients
            subject=subject,
            html_message=content,
            priority="now",  # High priority
        )

        return Response({"status": "sent"})
