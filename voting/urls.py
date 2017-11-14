from django.conf.urls import url, include
from rest_framework import routers

from voting import views

router = routers.DefaultRouter()
router.register(r'meetings', views.MeetingViewSet)
router.register(r'scanners', views.ScannerViewSet)
router.register(r'attendants', views.AttendantViewSet)
router.register(r'votes', views.VoteViewSet)
router.register(r'made_votes', views.MadeVoteViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]