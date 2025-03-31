"""
Staging settings are used to develop the backend when hosted remotely behind a webserver with HTTPS.
It does not implement login towards LiU as that requires specific settings to make LiU trust the login.
This requires accounts with passwords to allow login as with debug.
"""

from app.settings_production import *

STAGING = True
DEBUG = False
# Update this if more web apps need to access backend. Only accepts exact strings.
ALLOWED_HOSTS += [
    "localhost:8000",
]

# Update this is more web apps need to access backend. Allows wildcards.
CSRF_TRUSTED_ORIGINS += ["http://localhost:8000", "https://localhost:8000"]

DJANGO_LOG_LEVEL = "DEBUG"
