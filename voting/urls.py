from django.conf.urls import url, include
from django.urls import path
from rest_framework import routers

from voting import views

router = routers.DefaultRouter()
router.register(r"meetings", views.MeetingViewSet, base_name="meeting")
router.register(r"admin-meetings", views.MeetingAdminViewSet, base_name="admin-meeting")
router.register(r"attendants", views.AttendantViewSet)
router.register(r"votes", views.VoteViewSet, base_name="vote")
router.register(r"admin-votes", views.VoteAdminViewSet, base_name="admin-vote")
router.register(r"made_votes", views.MadeVoteViewSet, base_name="made_vote")

urlpatterns = [
    path(r"", include(router.urls)),
    path(r"speakers/<pk>", views.SpeakerRequestDetailView.as_view()),
    path(r"speakers/", views.SpeakerRequestView.as_view()),
    path(r"attend/", views.SelfAttendView.as_view()),
]
