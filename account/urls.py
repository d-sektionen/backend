from django.conf.urls import url

from account import views

import cas.views

urlpatterns = [
    url(r'^$', views.index),

    # CAS
    url(r'^login/$', cas.views.login, name='login'),
    url(r'^logout/$', cas.views.logout, name='logout'),
]
