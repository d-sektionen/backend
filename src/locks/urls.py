from django.conf.urls import url, include
from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(r"bettan", views.BettanViewSet, basename="bettan")
router.register(r"configura", views.ConfiguraViewSet, basename="config")

urlpatterns = [
    url(r"^", include(router.urls)),
]
