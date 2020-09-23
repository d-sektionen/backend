from django.conf.urls import url, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
# router.register(r"register", views.RegisterViewSet, base_name="register")
router.register(r"events", views.EventBaseViewSet, base_name="event")
router.register(r"doorkeepers", views.DoorkeeperViewSet, base_name="doorkeeper")
# router.register(r'attendants', views.AttendantViewSet)
# router.register(r'votes', views.VoteViewSet, base_name='vote')
# router.register(r'made_votes', views.MadeVoteViewSet, base_name='made_vote')

urlpatterns = [
    url(r"^", include(router.urls)),
    url(r"register/", views.RegisterView.as_view()),
]
