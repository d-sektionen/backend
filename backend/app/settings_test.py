import os
from dotenv import load_dotenv
from .settings_shared import *

dotenv_path = os.path.join(BASE_DIR, ".env")

load_dotenv(dotenv_path)

SECRET_KEY = "*3#2cxri$uc!5%#v+-9!h=yig-$@i-e!idod(d&9v6qf)bjv%!"
DEBUG = True
EMAIL_ENABLED = False
ALLOWED_HOSTS = ["*"]
AUTH_COOKIE_SECURE = False
MICROSOFT_CLIENT_ID = "test-client-id"
MICROSOFT_CLIENT_SECRET = "test-client-secret"
MICROSOFT_AUTHORITY = f"https://{MICROSOFT_LOGIN_HOST}/test-tenant"


# Database
# Tests run against Postgres by default: some tests need it (row locking, schema
# checks) and are silently skipped on SQLite. TEST_DATABASE=sqlite opts into a
# quick in-memory run that needs no database server.
if os.getenv("TEST_DATABASE") == "sqlite":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
else:
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

# No Redis in tests: sockets.py falls back to python-socketio's in-memory manager.
REDIS_URL = None

CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
