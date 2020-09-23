from django.conf.urls import url, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"log-entries", views.LogEntryViewSet, base_name="log_entry")

urlpatterns = [
    url(r"^", include(router.urls)),
    url(r"keys/", views.KeyView.as_view()),
]
