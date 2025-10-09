from django.conf.urls import include
from django.urls import path
from rest_framework import routers

from ..voting import views

router = routers.DefaultRouter()
router.register(r"meetings", views.MeetingViewSet, basename="meeting")
router.register(r"guest-meetings", views.MeetingGuestViewSet, basename="guest-meeting")
router.register(r"admin-meetings", views.MeetingAdminViewSet, basename="admin-meeting")
router.register(r"attendants", views.AttendantViewSet)
router.register(r"votes", views.VoteViewSet, basename="vote")
router.register(r"admin-votes", views.VoteAdminViewSet, basename="admin-vote")
router.register(r"made_votes", views.MadeVoteViewSet, basename="made_vote")

urlpatterns = [
    path(r"", include(router.urls)),
    path(r"speakers/<pk>", views.SpeakerRequestDetailView.as_view()),
    path(r"speakers/", views.SpeakerRequestView.as_view()),
    path(r"attend/", views.SelfAttendView.as_view()),
]
