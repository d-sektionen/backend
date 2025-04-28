import os
from django.conf import settings
from django.http import Http404, HttpResponse
from django.utils.http import unquote
from django.utils.encoding import smart_str
from rest_framework.views import APIView

from account.permissions import AllowMembers


class ProtectedMediaView(APIView):
    """
    Intercept all /media/ requests and protect them.
    """

    permission_classes = (AllowMembers,)

    def get(self, request, path):
        """
        Handle GET requests to serve protected media files.
        """
        # SECURITY: Prevent path traversal attacks
        normalized_path = os.path.normpath(unquote(path))
        if normalized_path.startswith(".."):
            raise Http404("Invalid path")

        full_path = os.path.join(settings.MEDIA_ROOT, normalized_path)

        if not os.path.exists(full_path):
            raise Http404("File does not exist")

        # Build X-Accel-Redirect path (important: matches nginx config)
        internal_path = f"/media/{normalized_path}"

        # Prepare response and send X-Accel-Redirect header to nginx
        response = HttpResponse()
        response["Content-Type"] = ""  # Let nginx detect it
        response["X-Accel-Redirect"] = smart_str(internal_path)
        return response
