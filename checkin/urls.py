from django.conf.urls import url, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'register', views.RegisterViewSet, base_name='register')
router.register(r'events', views.EventViewSet, base_name='event')
# router.register(r'scanners', views.ScannerViewSet)
# router.register(r'attendants', views.AttendantViewSet)
# router.register(r'votes', views.VoteViewSet, base_name='vote')
# router.register(r'made_votes', views.MadeVoteViewSet, base_name='made_vote')

urlpatterns = [
  url(r'^', include(router.urls)),
  # url(r'register/', views.Register),
]