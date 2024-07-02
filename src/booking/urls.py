from django.conf.urls import url, include
from rest_framework import routers
from .views import BookingViewSet, ItemViewSet

router = routers.DefaultRouter()
router.register(r'bookings', BookingViewSet)
router.register(r'items', ItemViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]