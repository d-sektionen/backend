from django.conf.urls import url, include
from rest_framework import routers

from carlogging import views

router = routers.DefaultRouter()
router.register(r'loggs', views.LoggingViewSet, base_name='loggs')

urlpatterns = [
    url(r'^', include(router.urls)),
]