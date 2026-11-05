import os
from dotenv import load_dotenv
from .settings_shared import *
from identity.django import Auth

dotenv_path = os.path.join(BASE_DIR, ".env")

load_dotenv(dotenv_path)

SECRET_KEY = "*3#2cxri$uc!5%#v+-9!h=yig-$@i-e!idod(d&9v6qf)bjv%!"
DEBUG = True
EMAIL_ENABLED = False
ALLOWED_HOSTS = ["*"]

MICROSOFT_IDENTITY = Auth(
    client_id="CLIENT_ID",
    client_credential="CLIENT_SECRET",
    # Source: https://identity-library.readthedocs.io/en/latest/django.html
    # This will be used to mount your project's auth views accordingly.
    # For example, if your input here is https://example.com/x/y/z/redirect,
    # then your project's redirect page will be mounted at '/x/y/z/redirect',
    # login page will be at '/x/y/z/login', and logout page will be at '/x/y/z/logout'.
    redirect_uri=f"{BASE_URL}/oauth2/callback",
    authority=f"https://{MICROSOFT_LOGIN_HOST}/LIU_TENANT_ID",
)


# Database
# TEST_DATABASE=postgres is an explicit switch (used by CI). Do not key this on
# POSTGRES_HOST: .env sets POSTGRES_HOST=postgres for Docker, which would break a
# plain local `python manage.py test`.
if os.getenv("TEST_DATABASE") == "postgres":
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
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }

# No Redis in tests: sockets.py falls back to python-socketio's in-memory manager.
REDIS_URL = None

CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
