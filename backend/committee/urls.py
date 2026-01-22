from django.conf.urls import include
from django.urls import re_path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(
    r"committeemembers/(?P<committee_id>.+)",
    views.CommitteeMembershipsViewSet,
    basename="committeemembers",
)
router.register(r"committees", views.CommitteesViewSet, basename="committee")

urlpatterns = [
    re_path(r"^", include(router.urls)),
]
