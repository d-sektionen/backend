from django.conf.urls import url, include
from rest_framework import routers

from account import views

import cas.views

router = routers.DefaultRouter()
router.register(r'user', views.UserViewSet, base_name='user')
router.register(r'section', views.SectionViewSet, base_name='section')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^token$', views.generate_token),

    # CAS
    url(r'^login/$', cas.views.login, name='login'),
    url(r'^logout/$', cas.views.logout, name='logout'),
]
