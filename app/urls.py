"""dsek URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import redirect_to_login
from django.urls import reverse

import account.urls
import voting.urls
import storage.urls
import booking.urls
import tools.urls
import checkin.urls
import attendance.urls

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.core import urls as wagtail_urls
from cms.api.api import api_router as cms_api_router

from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView

import cas.views

def redirect_to_my_auth(request):
    return redirect_to_login(reverse('wagtailadmin_home'), login_url='/account/login')

urlpatterns = [
    # Admin pages
    url(r'^admin/', admin.site.urls),

    # Account
    url(r'^account/', include(account.urls)),

    # Voting
    url(r'^voting/', include(voting.urls)),

    # Storage
    url(r'^storage/', include(storage.urls)),

    # Booking
    url(r'^booking/', include(booking.urls)),
    
    # Tools
    url(r'^tools/', include(tools.urls)),
    
    # Checkin
    url(r'^checkin/', include(checkin.urls)),

    # Attendance
    url(r'^attendance/', include(attendance.urls)),

    # CMS routes (Wagtail)
    url(r'^api/cms/', cms_api_router.urls),
    url(r'^cms/graphql', csrf_exempt(GraphQLView.as_view())),
    url(r'^cms/graphiql', csrf_exempt(GraphQLView.as_view(graphiql=True, pretty=True))),
    url(r'^cms/login', redirect_to_my_auth, name='wagtailadmin_login'),
    url(r'^cms/logout', cas.views.logout, name='wagtailadmin_logout'),
    url(r'^cms/', include(wagtailadmin_urls)),
    url(r'^documents/', include(wagtaildocs_urls)),
    url(r'^pages/', include(wagtail_urls))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # TODO: Change for production

# TODO: define custom error handlers https://www.django-rest-framework.org/api-guide/exceptions/#generic-error-views