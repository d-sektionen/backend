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
    1. from ..the include() function: from django.conf import urls as the include() function: from django.conf_urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import redirect_to_login
from django.urls import re_path, reverse

from ..account import urls as account_urls
from ..oauth2 import urls as oauth2_urls
from ..voting import urls as voting_urls
from ..booking import urls as booking_urls
from ..tools import urls as tools_urls
from ..checkin import urls as checkin_urls
from ..attendance import urls as attendance_urls
from ..membership import urls as membership_urls
from ..carlogging import urls as carlogging_urls
from ..keylog import urls as keylog_urls
from ..budgetportal import urls as budgetportal_urls
from ..committee import urls as committee_urls
from ..locks import urls as locks_urls


def redirect_to_my_auth(request):
    return redirect_to_login(reverse("wagtailadmin_home"), login_url="/account/login")


urlpatterns = [
    # Admin pages
    re_path(r"^admin/", admin.site.urls),
    # Account
    re_path(r"^account/", include(account_urls)),
    # Voting
    re_path(r"^voting/", include(voting_urls)),
    # Booking
    re_path(r"^booking/", include(booking_urls)),
    # Tools
    re_path(r"^tools/", include(tools_urls)),
    # Checkin
    re_path(r"^checkin/", include(checkin_urls)),
    # Attendance
    re_path(r"^attendance/", include(attendance_urls)),
    # Membership
    re_path(r"^membership/", include(membership_urls)),
    # Carloggin
    re_path(r"^carlogging/", include(carlogging_urls)),
    # Committee
    re_path(r"^committee/", include(committee_urls)),
    # Keylog
    re_path(r"^keylog/", include(keylog_urls)),
    # Keylog
    re_path(r"^budget/", include(budgetportal_urls)),
    # Locks
    re_path(r"^locks/", include(locks_urls)),
    # Login to backend
    re_path(r"^oauth2/", include(oauth2_urls)),
    settings.MICROSOFT_IDENTITY.urlpattern,
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
