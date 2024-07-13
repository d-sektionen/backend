from django.conf.urls import url, include
from rest_framework import routers

from . import views

urlpatterns = [url(r"request/", views.RequestView.as_view())]

