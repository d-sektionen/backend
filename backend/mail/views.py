from rest_framework import views
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from .view_helpers import generate_mail_context
from ..app.utils import render_email
from post_office import mail

# from django.contrib.auth.models import User
from ..account.models import Profile

# NOTE: booking views.py har logik för att skicka mail


class PreviewView(views.APIView):
    renderer_classes = [TemplateHTMLRenderer]

    def post(self, request):
        content = request.data.get("content", "")
        context = generate_mail_context(content)

        return Response(context, template_name="email/newsletter.html")


class SendView(views.APIView):
    def post(self, request):
        context = generate_mail_context(
            request.data.get("content", ""), request.data.get("subject", "Infomail")
        )
        # Notify the user that the booking has been denied.
        subject, content = render_email("email/newsletter", context)

        mail_recipients: list[str] = list(
            Profile.objects.filter(infomail_subscriber=True).values_list(
                "user__email", flat=True
            )
        )
        print(
            mail.send(
                recipients=mail_recipients,
                subject=subject,
                html_message=content,
                priority="now",  # High priority
            )
        )

        return Response({"status": "sent"})
