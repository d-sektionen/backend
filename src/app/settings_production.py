import os

from app.settings_shared import *

SECRET_KEY = os.getenv("SECRET_KEY", "INSECURE_SECRET_KEY")
DEBUG = False

EMAIL_ENABLED = True
EMAIL_HOST = "localhost"
SERVER_EMAIL = "no-reply@d-sektionen.se"

ADMINS = (("WebbU", "webbutskottet@d.lintek.liu.se"),)

ALLOWED_HOSTS = ["*"]

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


SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
CSRF_COOKIE_HTTPONLY = True
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
        "file": {
            "level": DJANGO_LOG_LEVEL,
            "class": "logging.FileHandler",
            "filename": "/var/log/backend-django.log",
            "formatter": "timestamp",
        },
    },
    "root": {
        "handlers": ["file"],
        "level": DJANGO_LOG_LEVEL,
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": DJANGO_LOG_LEVEL,
        },
    },
}
