from django.conf.urls import url, include
from rest_framework import routers

from . import views

urlpatterns = [
    url(r'calendar', views.section_calendar),
    url(r'netlight', views.netlight),
    url(r'nginx-member-protect', views.member_only_accel_redirect)
]