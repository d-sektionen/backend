from django.conf.urls import include
from django.urls import re_path
from rest_framework import routers
from .views import BookingViewSet, ItemPoolViewSet

router = routers.DefaultRouter()
router.register(r"bookings", BookingViewSet)
router.register(r"itemPools", ItemPoolViewSet)

urlpatterns = [
    re_path(r"^", include(router.urls)),
]
