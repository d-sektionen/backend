from django.conf.urls import include
from django.urls import re_path
from rest_framework import routers
from . import views


router = routers.DefaultRouter()
router.register(r"status", views.StatusViewSet, basename="status")
urlpatterns = [
    url(r"^", include(router.urls)),
    url(r"calendar", views.SectionCalendarViewSet),
]
