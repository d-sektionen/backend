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
from django.contrib import admin

import account.urls
import voting.urls
import storage.urls
import booking.urls
import tools.urls

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
]
