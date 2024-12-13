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

from django.conf.urls import include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import redirect_to_login
from django.urls import re_path, reverse

import account.urls
import voting.urls
import booking.urls
import tools.urls
import checkin.urls
import attendance.urls
import membership.urls
import carlogging.urls
import keylog.urls
import budgetportal.urls
import committee.urls
import locks.urls
import email.urls


def redirect_to_my_auth(request):
    return redirect_to_login(reverse("wagtailadmin_home"), login_url="/account/login")


urlpatterns = [
    # Admin pages
    re_path(r"^admin/", admin.site.urls),
    # Account
    re_path(r"^account/", include(account.urls)),
    # Voting
    re_path(r"^voting/", include(voting.urls)),
    # Booking
    re_path(r"^booking/", include(booking.urls)),
    # Tools
    re_path(r"^tools/", include(tools.urls)),
    # Checkin
    re_path(r"^checkin/", include(checkin.urls)),
    # Attendance
    re_path(r"^attendance/", include(attendance.urls)),
    # Membership
    re_path(r"^membership/", include(membership.urls)),
    # Carloggin
    re_path(r"^carlogging/", include(carlogging.urls)),
    # Committee
    re_path(r"^committee/", include(committee.urls)),
    # Keylog
    re_path(r"^keylog/", include(keylog.urls)),
    # Keylog
    re_path(r"^budget/", include(budgetportal.urls)),
    # Locks
    re_path(r"^locks/", include(locks.urls)),
    # Infomail
    re_path(r"^infomail/", include(email.urls)),
    # Login to backend
    re_path("oauth2/", include("django_auth_adfs.urls")),
] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)  # TODO: Change for production

# TODO: define custom error handlers https://www.django-rest-framework.org/api-guide/exceptions/#generic-error-views
# handler500 = 'rest_framework.exceptions.server_error'
# handler400 = 'rest_framework.exceptions.bad_request'
