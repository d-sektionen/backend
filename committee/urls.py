from django.conf.urls import include, url
from django.urls import path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"", views.CommitteeViewSet, basename="committees")

urlpatterns = [
    url(r"^", include(router.urls)),
]
