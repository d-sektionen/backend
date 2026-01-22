from django.conf.urls import include
from django.urls import re_path
from rest_framework import routers
from .views import BookingViewSet, ItemViewSet

router = routers.DefaultRouter()
router.register(r"bookings", BookingViewSet)
router.register(r"items", ItemViewSet)

urlpatterns = [
    re_path(r"^", include(router.urls)),
]
