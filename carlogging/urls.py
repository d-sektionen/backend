from django.conf.urls import url, include
from django.urls import path
from rest_framework import routers

from carlogging import views

router = routers.DefaultRouter()
router.register(r'starts', views.LogStartViewSet, basename='starts')
router.register(r'entries', views.LogEntryViewSet, basename='entries')

urlpatterns = [
    url(r'^', include(router.urls)),
    path(r'entries/<int:entry_id>/pdf-export', views.export_entry_pdf),
]
