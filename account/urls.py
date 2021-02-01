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
router.register(
    r"calendar-subscriptions",
    views.CalendarSubscriptionViewSet,
    basename="calendar-subscription",
)

urlpatterns = [
    # Router paths
    path(r"", include(router.urls)),
    # User related
    path(r"me/", views.MeView.as_view()),
    path(r"profile/", views.ProfileView.as_view()),
    path(r"identification-token/", views.IdentificationTokenView.as_view()),
    path(r"infomail-subscribers/", views.InfomailSubscriberView.as_view()),
    path(r"infomail-everyone/", views.InfomailEveryoneView.as_view()),
    # JWT Login
    path(r"token/", views.generate_token),
    path(r"token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Login with credentials, also returns JWT
    path(r"credential-login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path(r"calendar/<uuid:pk>", views.CalendarFeed(), name="calendar_feed"),
    # CAS
    path(r"login/", cas.views.login, name="login"),
    path(r"logout/", cas.views.logout, name="logout"),
]
