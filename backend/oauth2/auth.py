import logging
import re
import urllib.parse as urlparse

from ..account.user import get_or_create_user
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME, login, logout
from django.contrib.auth.models import User, update_last_login
from django.http import HttpRequest, HttpResponseRedirect
from django.utils.encoding import iri_to_uri
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError, AuthenticationFailed

import requests

logger = logging.getLogger(__name__)

AUTH = settings.MICROSOFT_IDENTITY
ALLOWED_HOSTS = settings.ALLOWED_HOSTS
SCOPES = ["User.Read"]
LIU_ID_REGEX = re.compile(r"[a-z]{4,5}[0-9]{2,3}")
DEFAULT_REDIRECT = "/"


def is_safe_redirect_url(url, allowed_domains, require_https=False):
    """Custom implementation of djangos url_has_allowed_host_and_scheme."""
    url_parts = urlparse.urlparse(url)

    if url_parts.netloc not in allowed_domains:
        return False

    if require_https and url_parts.scheme != "https":
        return False

    return True


def get_me(token):
    me = requests.get(
        "https://graph.microsoft.com/v1.0/me",
        headers={"Authorization": "Bearer " + token},
        timeout=30,
    )

    if me.status_code != 200:
        logger.warning(
            f"Failed to fetch user profile from Microsoft Graph API: {me.text}"
        )
        return {}

    return me.json()


def external_auth_callback_login(request):
    if request.user.is_authenticated:
        logger.debug(f"Reauthenticating user: {request.user}\n")

    response = AUTH.auth_response(request)

    if not isinstance(response, HttpResponseRedirect):
        logger.warning("Auth error occurred at Entra ID endpoint")
        logger.warning(response.content)
        return response, None

    # FIXME: Use of internal function, should look for alternative
    auth = AUTH._build_auth(request.session)
    identity_user = auth.get_user()

    # This should always be a liu email, but for reliability reasons no assumptions
    # are made thus try to search for liu-id with regex.
    preferred_username = identity_user.get("preferred_username", "")
    match = LIU_ID_REGEX.search(preferred_username)
    liu_id = match.group() if match else None

    if not liu_id:
        logger.warning(
            f"A LiU-ID could not be extracted when trying to login Entra ID user {preferred_username}"
        )
        # Unsure if returning response is correct or just return 401...
        return response, None

    django_user, _ = get_or_create_user(liu_id)

    # Update fields from Entra ID
    token = auth.get_token_for_user(SCOPES)
    me = get_me(token.get("access_token"))
    if len(me) > 0:
        first_name = me.get("givenName", "")
        last_name = me.get("surname", "")
        email = me.get("mail", "")

        django_user.first_name = first_name
        django_user.last_name = last_name
        django_user.email = email
        django_user.save()
    else:
        logger.warning(
            f"Failed to fetch user profile from Microsoft Graph API for user {preferred_username}"
        )

    login(request, django_user, backend="django.contrib.auth.backends.ModelBackend")
    update_last_login(None, django_user)
    logger.debug(f"Django user login: {django_user}")

    return response, django_user


def auth_logout(request):
    logout(request=request)
    # WARN: One might be tempted to use AUTH.logout here, but that will cause
    # the user to be logged out from Entra, not just our backend.


def get_safe_redirect(request: HttpRequest):
    path = request.get_full_path()

    redirect_url = request.GET.get(REDIRECT_FIELD_NAME, path)

    url_is_safe = is_safe_redirect_url(redirect_url, ALLOWED_HOSTS, require_https=False)

    if url_is_safe is False:
        redirect_url = DEFAULT_REDIRECT

    return iri_to_uri(redirect_url)


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        access_token = request.COOKIES.get("access_token")

        if access_token is None:
            return None

        try:
            validated_token = self.get_validated_token(access_token)
        except (
            TokenError,
            AuthenticationFailed,
        ) as _:  # catches InvalidToken, ExpiredToken, etc.
            return None

        return self.get_user(validated_token), validated_token
