from rest_framework import views
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from .view_helpers import week_number, get_events

# NOTE: booking views.py har logik för att skicka mail


class GenerateView(views.APIView):
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request, format=None):
        context = {
            "week_number": week_number(),
            "events": get_events(),
        }

        # context = {
        #     "week_number": 1000,
        #     "events": [{"title": "arst", "start": "arst", "end": "arst"}],
        # }

        # html_code = render_to_string("mail/base.html", context)
        return Response(context, template_name="mail/base.html")
        # return Response(
        #     html_code, content_type="text/html", headers={"Content-Type": "text/html"}
        # )
