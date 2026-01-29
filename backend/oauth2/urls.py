from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    ExternalAuthCallbackView,
    LoginView,
    LogoutView,
)

urlpatterns = [
    path(r"login/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path(r"login", LoginView.as_view(), name="login"),
    path(r"logout", LogoutView.as_view(), name="logout"),
    path(
        r"callback",
        ExternalAuthCallbackView.as_view(),
        name="external_auth_callback",
    ),
]
