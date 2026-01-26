"""
Shared settings are settings that all configurations use. They have to be as common as possible.
Overwriting settings sometimes happens in sub setting files.
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import datetime
import os

from dotenv import load_dotenv
from corsheaders.defaults import default_headers
from identity.django import Auth

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

dotenv_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path)

# Application definition

INSTALLED_APPS = [
    # ---
    # Project apps
    # ---
    "backend.account",
    "backend.voting.apps.VotingConfig",
    "backend.tools",
    "backend.locks",
    "backend.membership",
    "backend.booking",
    "backend.logger",
    "backend.checkin",
    "backend.attendance",
    "backend.carlogging",
    "backend.committee",
    "backend.keylog",
    "backend.budgetportal",
    "backend.oauth2",
    # ---
    # Django related
    # ---
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "imagekit",
    "post_office",
    "identity",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

MICROSOFT_LOGIN_HOST = "login.microsoftonline.com"
APP_HOSTNAME = os.getenv("APP_HOSTNAME")
AUTHENTICATION_BACKENDS = ("django.contrib.auth.backends.ModelBackend",)
# Configure django to redirect users to the right URL for login
# SCOPE = "User.Read"
LOGIN_EXEMPT_URLS = []
MICROSOFT_IDENTITY = Auth(
    client_id=os.getenv("CLIENT_ID"),
    client_credential=os.getenv("CLIENT_SECRET"),
    # Source: https://identity-library.readthedocs.io/en/latest/django.html
    # This will be used to mount your project's auth views accordingly.
    # For example, if your input here is https://example.com/x/y/z/redirect,
    # then your project's redirect page will be mounted at '/x/y/z/redirect',
    # login page will be at '/x/y/z/login', and logout page will be at '/x/y/z/logout'.
    redirect_uri=f"http://{APP_HOSTNAME}/oauth2/callback",
    authority=f"https://{MICROSOFT_LOGIN_HOST}/{os.getenv("LIU_TENANT_ID")}",
)

ALLOWED_HOSTS = [
    APP_HOSTNAME,
    MICROSOFT_LOGIN_HOST,
    "medlem.d-sektionen.se",
    # NOTE: localhost is added twice due to some parts caring about port and some not.
    "localhost",
    "localhost:4000",
]

ROOT_URLCONF = "backend.app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    },
    {
        "BACKEND": "post_office.template.backends.post_office.PostOfficeTemplates",
        "APP_DIRS": True,
        "DIRS": [],
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.template.context_processors.request",
            ]
        },
    },
]

WSGI_APPLICATION = "backend.app.wsgi.application"


# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Stockholm"
USE_I18N = True
USE_TZ = True


STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (os.path.join(BASE_DIR, "app", "static"),)

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

# Django REST Framework
REST_FRAMEWORK = {
    # Sets default permission requirements (403 errors) for every endpoint. Override in viewset, as shown in cms.api
    "DEFAULT_PERMISSION_CLASSES": (
        "backend.app.permissions.AllowOptionsAuthentication",
    ),
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        # JWT for api access
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        # Session auth for admin access
        "rest_framework.authentication.SessionAuthentication",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": datetime.timedelta(seconds=10),
    "REFRESH_TOKEN_LIFETIME": datetime.timedelta(hours=12),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    # To allow some wiggleroom for clients to retireve new tokens. This accounts for unsynced clocks and network delay.
    "LEEWAY": 60,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
}

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Home Assistant API (Locks)
BETTAN_LOCK_ID = os.getenv("BETTAN_LOCK_ID")
CONFIGURA_LOCK_ID = os.getenv("CONFIGURA_LOCK_ID")
HOME_ASSISTANT_TOKEN = os.getenv("HOME_ASSISTANT_TOKEN")
HOME_ASSISTANT_BASEURL = os.getenv("HOME_ASSISTANT_BASEURL")

GATSBY_MANAGER_URL = os.getenv("GATSBY_MANAGER_URL")

# TODO: maybe a bit more limited CORS.
CORS_ORIGIN_ALLOW_ALL = True
CORS_EXPOSE_HEADERS = [*default_headers, "retry-after"]

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": datetime.timedelta(days=5),
    "REFRESH_TOKEN_LIFETIME": datetime.timedelta(days=15),
}

# LOGIN_URL = "/account/login/"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# URL to D-sektionens calendar
CAL_URL = os.getenv(
    "CAL_URL",
    "https://calendar.google.com/calendar/ical/webmaster%40d.lintek.liu.se/public/basic.ics",
)


EMAIL_BACKEND = "post_office.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "localhost")
EMAIL_PORT = os.environ.get("EMAIL_PORT", 587)
EMAIL_HOST_USER = os.getenv("EMAIL_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@d-sektionen.se")
