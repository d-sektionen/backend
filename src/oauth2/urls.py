from django.conf import settings
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView

from .views import (
    BlacklistView,
    ExternalAuthCallbackView,
    LoginView,
    LogoutView,
    RefreshView,
)

urlpatterns = [
    path(r"refresh", RefreshView.as_view(), name="token_refresh"),
]

# Production/staging settings
if settings.DEBUG or settings.STAGING:
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
