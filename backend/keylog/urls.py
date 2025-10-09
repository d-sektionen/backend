from django.conf.urls import include
from django.urls import re_path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"log-entries", views.LogEntryViewSet, basename="log_entry")

urlpatterns = [
    re_path(r"^", include(router.urls)),
    re_path(r"keys/", views.KeyView.as_view()),
]
