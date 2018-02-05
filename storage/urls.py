from django.conf.urls import url, include
from rest_framework import routers

from storage import views

router = routers.DefaultRouter()

router.register(r'storageroom', views.StorageRoomViewSet)
router.register(r'location', views.LocationViewSet)
router.register(r'booking', views.BookingViewSet)
router.register(r'object', views.ObjectViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]