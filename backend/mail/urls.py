from django.urls import path
from .views import PreviewView, SendView, SendSelfView

# router = routers.DefaultRouter()
# router.register(r"generate", GenerateView)

urlpatterns = [
    path("preview/", PreviewView.as_view()),
    path("send/", SendView.as_view()),
    path("send-self/", SendSelfView.as_view()),
    # re_path(r"^", include(router.urls)),
]
