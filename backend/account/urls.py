from django.conf.urls import include
from django.urls import path
from rest_framework import routers

from ..account import views
from .feeds import CalendarFeed

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
    path(r"profile/<int:pk>/", views.ProfileView.as_view()),
    path(r"profile/me/", views.MeProfileView.as_view()),
    path(r"infomail-subscribers/", views.InfomailSubscriberView.as_view()),
    path(r"infomail-everyone/", views.InfomailEveryoneView.as_view()),
    path(r"calendar/<uuid:pk>", CalendarFeed(), name="calendar_feed"),
]
