from django.urls import path
from .views import PreviewView, SendView, SendSelfView

urlpatterns = [
    path("preview/", PreviewView.as_view()),
    path("send/", SendView.as_view()),
    path("send-self/", SendSelfView.as_view()),
]
