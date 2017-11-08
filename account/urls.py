from django.conf.urls import url

from account import views

import cas.views

urlpatterns = [
    url(r'^token$', views.generate_token),

    # CAS
    url(r'^login/$', cas.views.login, name='login'),
    url(r'^logout/$', cas.views.logout, name='logout'),
]
