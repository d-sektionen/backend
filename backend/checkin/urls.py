from django.conf.urls import include
from django.urls import re_path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
# router.register(r"register", views.RegisterViewSet, basename="register")
router.register(r"events", views.EventBaseViewSet, basename="event")
router.register(r"doorkeepers", views.DoorkeeperViewSet, basename="doorkeeper")
# router.register(r'attendants', views.AttendantViewSet)
# router.register(r'votes', views.VoteViewSet, basename='vote')
# router.register(r'made_votes', views.MadeVoteViewSet, basename='made_vote')

urlpatterns = [
    re_path(r"^", include(router.urls)),
    re_path(r"register/", views.RegisterView.as_view()),
]
