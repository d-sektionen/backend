from django.conf.urls import url, include
from rest_framework import routers

from voting import views

router = routers.DefaultRouter()
#Add urls here router.register(r'[URL]', views.[Object]ViewSet, base_name='[Name]')

urlpatterns = [
    url(r'^', include(router.urls)),
]