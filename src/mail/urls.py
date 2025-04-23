from django.conf.urls import include
from django.urls import re_path
from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(r"mail-template", views.MailTemplateViewSet, basename="mail-template")
router.register(r"mail", views.MailViewSet, basename="mail")

urlpatterns = [
    re_path(r"^", include(router.urls)),
]
