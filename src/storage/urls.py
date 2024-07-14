from django.conf.urls import include
from django.urls import re_path
from rest_framework import routers

from storage import views

router = routers.DefaultRouter()

router.register(r"storageroom", views.StorageRoomViewSet)
router.register(r"location", views.LocationViewSet)
router.register(r"booking", views.BookingViewSet)
router.register(r"object", views.ObjectViewSet)

urlpatterns = [
    re_path(r"^", include(router.urls)),
]
