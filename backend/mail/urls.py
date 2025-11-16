from django.conf.urls import include
from django.urls import re_path, path
from rest_framework import routers
from .views import PreviewView

router = routers.DefaultRouter()
# router.register(r"generate", GenerateView)

urlpatterns = [
    path("preview", PreviewView.as_view()),
    re_path(r"^", include(router.urls)),
]
