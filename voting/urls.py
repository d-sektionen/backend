from django.conf.urls import url, include
from rest_framework import routers

from voting import views

router = routers.DefaultRouter()
router.register(r'sections', views.SectionViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]