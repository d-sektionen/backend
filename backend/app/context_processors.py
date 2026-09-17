from django.conf import settings


def export_settings(request):
    """A context processor to export settings to templates.
    Currently only exports BASE_URL, but can be extended to include more settings as needed.
    """
    return {
        "BASE_URL": settings.BASE_URL,
    }
