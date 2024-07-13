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
        "ENGINE": "django.db.backends.postgresql_psycopg2",
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

# Log errors to Heroku log
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "ERROR"),
        },
    },
}

# Currently configured for Heroku. Might want to re-configure for deployment on d-sektionen.se.
CHANNEL_LAYERS["default"]["BACKEND"] = "asgi_redis.RedisChannelLayer"
CHANNEL_LAYERS["default"]["CONFIG"] = {
    "hosts": [os.environ.get("REDIS_URL", "redis://localhost:6379")],
}
