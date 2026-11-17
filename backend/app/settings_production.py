"""
Production settings are used for live deployment behind a webserver and using HTTPS.
This enables login towards LiU with the prerequisite that the hostname in the webserver is
either backend.d-sektionen.se or backend.dev.d-sektionen.se (update this if changed).

To develop the login towards LiU, ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS have to be updated with hosts
that you use to develop with. If you are using a localhost hosted frontend you have to add localhost:<port>.
"""

import os

from ..app.settings_shared import *

SECRET_KEY = os.getenv("SECRET_KEY", "INSECURE_SECRET_KEY")
DEBUG = False
STAGING = False

EMAIL_ENABLED = True
SERVER_EMAIL = "no-reply@d-sektionen.se"

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

# Update this if more web apps need to access backend. Only accepts exact strings.
ALLOWED_HOSTS = ALLOWED_HOSTS + [
    "medlem.d-sektionen.se",
    "medlem.dev.d-sektionen.se",
    "backend.d-sektionen.se",
    "backend.dev.d-sektionen.se",
]

X_FRAME_OPTIONS = "DENY"

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

AUTH_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

CORS_ALLOWED_ORIGINS = [f"https://{host}" for host in ALLOWED_HOSTS]
CSRF_TRUSTED_ORIGINS = [f"https://{host}" for host in ALLOWED_HOSTS]
