from django.conf import settings
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    BlacklistView,
    ExternalAuthCallbackView,
    LoginView,
    LogoutView,
)

urlpatterns = [
    path(r"login/refresh", TokenRefreshView.as_view(), name="token_refresh"),
]

# Production/staging settings
# TODO: remove True
if False and settings.DEBUG:
    urlpatterns += [
        path(r"login", TokenObtainPairView.as_view(), name="login"),
        path(r"logout", BlacklistView.as_view(), name="logout"),
    ]
else:
    urlpatterns += [
        path(r"login", LoginView.as_view(), name="login"),
        path(r"logout", LogoutView.as_view(), name="logout"),
        path(
            r"callback",
            ExternalAuthCallbackView.as_view(),
            name="external_auth_callback",
        ),
    ]
