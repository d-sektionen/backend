from django.conf.urls import url, include
from rest_framework import routers

from carlogging import views

router = routers.DefaultRouter()
router.register(r"entries", views.LogEntryViewSet, base_name="entries")

urlpatterns = [url(r"^", include(router.urls))]

