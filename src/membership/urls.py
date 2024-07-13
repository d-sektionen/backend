from django.conf.urls import url

from . import views

urlpatterns = [url(r"request/", views.RequestView.as_view())]

