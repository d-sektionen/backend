from django.conf.urls import url

from . import views


urlpatterns = [
    url(r"calendar", views.section_calendar),
]
