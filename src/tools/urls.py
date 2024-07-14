from django.conf.urls import include
from django.urls import re_path
from rest_framework import routers
from . import views


router = routers.DefaultRouter()
router.register(r"status", views.StatusViewSet, basename="status")
urlpatterns = [
    re_path(r"^", include(router.urls)),
    re_path(r"calendar", views.section_calendar),
]
