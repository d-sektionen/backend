from django.conf.urls import url, include
from django.urls import path
from rest_framework import routers

from carlogging import views

router = routers.DefaultRouter()
router.register(r"entries", views.LogEntryViewSet, basename="entries")
router.register(r"starts", views.LogStartViewSet, basename="starts")
# router.register(r"pdf-export", views.pdf_export, basename="pdf-export")

urlpatterns = [
    url(r"^", include(router.urls)),
    path(r"pdf-export/<int:entry_id>", views.PdfExport.as_view()),
]
