from django.conf.urls import url, include
from rest_framework import routers
from . import views


router = routers.DefaultRouter()
router.register(r"status", views.StatusViewSet, basename="status")
urlpatterns = [
    url(r"^", include(router.urls)),
    url(r"calendar", views.section_calendar),
]
