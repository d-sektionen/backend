from django.conf.urls import url, include
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from account import views


import cas.views

router = routers.DefaultRouter()
router.register(r'user', views.UserViewSet, base_name='user')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^token/$', views.generate_token),
    url(r'^token/refresh/$', TokenRefreshView.as_view(), name='token_refresh'),
    # Login with credentials
    url(r'^credential-login/$', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    # CAS
    url(r'^login/$', cas.views.login, name='login'),
    url(r'^logout/$', cas.views.logout, name='logout'),
]
