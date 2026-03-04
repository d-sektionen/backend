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

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

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


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
