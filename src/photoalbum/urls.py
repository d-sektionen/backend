from django.conf.urls import include
from django.urls import re_path
from rest_framework import routers

from photoalbum.views import PhotoViewSet

router = routers.DefaultRouter()
router.register(r"photos", PhotoViewSet)

urlpatterns = [
    re_path(r"^", include(router.urls)),
]
