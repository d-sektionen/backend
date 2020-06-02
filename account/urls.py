from django.conf.urls import url, include
from django.urls import path
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from account import views


import cas.views

router = routers.DefaultRouter()
router.register(r"user", views.UserViewSet, base_name="user")
router.register(
    r"calendar-subscriptions",
    views.CalendarSubscriptionViewSet,
    base_name="calendar-subscription",
)

urlpatterns = [
    path(r"", include(router.urls)),
    path(r"token/", views.generate_token),
    path(r"token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path(r"calendar/<uuid:pk>", views.CalendarFeed(), name="calendar_feed"),
    # Login with credentials
    path(r"credential-login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    # CAS
    path(r"login/", cas.views.login, name="login"),
    path(r"logout/", cas.views.logout, name="logout"),
]
