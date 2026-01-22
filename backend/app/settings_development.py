from dotenv import load_dotenv
from .settings_shared import *

dotenv_path = os.path.join(BASE_DIR, ".env")

load_dotenv(dotenv_path)

SECRET_KEY = "*3#2cxri$uc!5%#v+-9!h=yig-$@i-e!idod(d&9v6qf)bjv%!"
DEBUG = True
EMAIL_ENABLED = False
ALLOWED_HOSTS = ["*"]

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
