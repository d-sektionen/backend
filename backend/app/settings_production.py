"""
Production settings are used for live deployment behind a webserver and using HTTPS.
This enables login towards LiU with the prerequisite that the hostname in the webserver is
either backend.d-sektionen.se or backend.dev.d-sektionen.se (update this if changed).

To develop the login towards LiU, ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS have to be updated with hosts
that you use to develop with. If you are using a localhost hosted frontend you have to add localhost:<port>.
"""

import os

from identity.django import Auth

from app.settings_shared import *

SECRET_KEY = os.getenv("SECRET_KEY", "INSECURE_SECRET_KEY")
DEBUG = False
STAGING = False

EMAIL_ENABLED = True
SERVER_EMAIL = "no-reply@d-sektionen.se"

INSTALLED_APPS += [
    "oauth2",
    "identity",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_NAME", "django"),
        "USER": os.getenv("POSTGRES_USER", "django"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "django"),
        "HOST": os.getenv("POSTGRES_HOST", "localhost"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}


MICROSOFT_LOGIN_HOST = "login.microsoftonline.com"
APP_HOSTNAME = os.getenv("APP_HOSTNAME")
assert APP_HOSTNAME is not None, "APP_HOSTNAME has to be set (localhost:<port> for dev)"
# Update this if more web apps need to access backend. Only accepts exact strings.
ALLOWED_HOSTS = [
    APP_HOSTNAME,
    MICROSOFT_LOGIN_HOST,
    "medlem.d-sektionen.se",
    "localhost:8000",
]

X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

# Update this is more web apps need to access backend. Allows wildcards.
CSRF_TRUSTED_ORIGINS = [f"https://{host}" for host in ALLOWED_HOSTS] + [
    "http://localhost:8000"
]

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
    redirect_uri=f"https://{APP_HOSTNAME}/oauth2/callback",
    authority=f"https://{MICROSOFT_LOGIN_HOST}/{os.getenv("LIU_TENANT_ID")}",
)

# Enable file logging for all loggers. Change level with this env variable.
DJANGO_LOG_LEVEL = os.getenv("DJANGO_LOG_LEVEL", "INFO")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "timestamp": {
            "format": "[{levelname}] {asctime} ({module}): {message}",
            "style": "{",
        },
    },
    "handlers": {
        "rotating_file": {
            "level": DJANGO_LOG_LEVEL,
            "formatter": "timestamp",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/var/log/backend-django.log",
            "mode": "a",
            "maxBytes": 1024 * 1024 * 5,  # 5MB
            "backupCount": 5,
        },
    },
    "root": {
        "handlers": ["rotating_file"],
        "level": DJANGO_LOG_LEVEL,
    },
    "loggers": {
        "django": {
            "handlers": ["rotating_file"],
            "level": DJANGO_LOG_LEVEL,
        },
    },
}
