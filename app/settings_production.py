from app.settings_shared import *

SECRET_KEY = os.getenv('SECRET_KEY', 'INSECURE_SECRET_KEY')
DEBUG = False

EMAIL_ENABLED = True
EMAIL_HOST = 'localhost'
SERVER_EMAIL = 'no-reply@d-sektionen.se'

ADMINS = (
    ('WebbU', 'webbutskottet@d.lintek.liu.se'),
)

ALLOWED_HOSTS = ['*']

# TODO: Configure
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '127.0.0.1',
        'USER': 'api',
        'PASSWORD': os.getenv('DB_PASS'),
        'NAME': 'api'
    }
}

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'DENY'
