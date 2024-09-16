from django.urls import re_path

from . import views

urlpatterns = [re_path(r"request/", views.RequestView.as_view())]
