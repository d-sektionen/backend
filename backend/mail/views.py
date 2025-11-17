from rest_framework import views
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from .view_helpers import sanitize_html, week_number, get_events
from django.utils.safestring import mark_safe
from django.conf import settings

# NOTE: booking views.py har logik för att skicka mail


class PreviewView(views.APIView):
    renderer_classes = [TemplateHTMLRenderer]

    def post(self, request):
        content = request.data.get("content", "")
        safe_content = mark_safe(sanitize_html(content))

        context = {
            "week_number": week_number(),
            "events": get_events(),
            "content": safe_content,
            "dsektionen_website_url": settings.INFO_D_SEKTIONEN_WEBSITE_URL,
            "dsektionen_info_email": settings.INFO_D_SEKTIONEN_INFO_EMAIL,
            "dsektionen_gdpr_url": settings.INFO_D_SEKTIONEN_GDPR_URL,
            "dsektionen_logo_url": settings.INFO_D_SEKTIONEN_LOGO_URL,
            "dsektionen_unsubscribe_url": settings.INFO_D_SEKTIONEN_UNSUBSCRIBE_URL,
            "dsektionen_instagram_url": settings.INFO_D_SEKTIONEN_INSTAGRAM_URL,
            "dsektionen_facebook_url": settings.INFO_D_SEKTIONEN_FACEBOOK_URL,
            "dsektionen_facebook_group_url": settings.INFO_D_SEKTIONEN_FACEBOOK_GROUP_URL,
            "dsektionen_more_social_media_url": settings.INFO_D_SEKTIONEN_MORE_SOCIAL_MEDIA_URL,
        }

        # preview = render_to_string("mail/base.html", context)
        # return Response({"preview": preview})
        return Response(context, template_name="mail/base.html")
