from django.conf.urls import include
from django.urls import re_path
from rest_framework import routers

from carlogging import views

router = routers.DefaultRouter()
router.register(r"entries", views.LogEntryViewSet, basename="entries")

urlpatterns = [re_path(r"^", include(router.urls))]
