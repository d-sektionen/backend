from dotenv import load_dotenv
from .settings_shared import *
from identity.django import Auth

dotenv_path = os.path.join(BASE_DIR, ".env")

load_dotenv(dotenv_path)

# Configure django to redirect users to the right URL for login
# SCOPE = "User.Read"
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

ALLOWED_HOSTS = ALLOWED_HOSTS + [
    # NOTE: localhost is added twice due to some parts caring about port and some not.
    "localhost",
    "localhost:4000",
]
SECRET_KEY = "*3#2cxri$uc!5%#v+-9!h=yig-$@i-e!idod(d&9v6qf)bjv%!"
DEBUG = True
EMAIL_ENABLED = False

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_NAME"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST"),
        "PORT": os.getenv("POSTGRES_PORT"),
    }
}


CORS_ALLOWED_ORIGINS = ["http://localhost:4000"]
