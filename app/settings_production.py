from app.settings_shared import *
import dj_database_url

SECRET_KEY = os.getenv('SECRET_KEY', 'INSECURE_SECRET_KEY')
DEBUG = False

EMAIL_ENABLED = True
EMAIL_HOST = 'localhost'
SERVER_EMAIL = 'no-reply@d-sektionen.se'

ADMINS = (
    ('WebbU', 'webbutskottet@d.lintek.liu.se'),
)

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': dj_database_url.config(conn_max_age=500)
}

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'DENY'
