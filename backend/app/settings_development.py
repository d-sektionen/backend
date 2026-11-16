from dotenv import load_dotenv
from .settings_shared import *

dotenv_path = os.path.join(BASE_DIR, ".env")

load_dotenv(dotenv_path)

ALLOWED_HOSTS = ALLOWED_HOSTS + [
    # NOTE: localhost is added twice due to some parts caring about port and some not.
    "localhost",
    "localhost:4000",
    "localhost:8000",
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

AUTH_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

CORS_ALLOWED_ORIGINS = [f"http://{host}" for host in ALLOWED_HOSTS]
CSRF_TRUSTED_ORIGINS = [f"http://{host}" for host in ALLOWED_HOSTS]
