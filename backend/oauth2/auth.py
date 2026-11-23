import logging
import re

from ..account.user import get_or_create_user
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME, login, logout
from django.contrib.auth.models import update_last_login
from django.http import HttpRequest, HttpResponseBadRequest, HttpResponseRedirect
from django.utils.encoding import iri_to_uri
from django.utils.http import url_has_allowed_host_and_scheme
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError, AuthenticationFailed
from django.middleware.csrf import CsrfViewMiddleware
from django.core.exceptions import PermissionDenied
import requests

from .entra import LoginError, complete_login

logger = logging.getLogger(__name__)

LIU_ID_REGEX = re.compile(r"[a-z]{4,5}[0-9]{2,3}")
DEFAULT_REDIRECT = "/"


def is_safe_redirect_url(url, allowed_domains, require_https=False):
    return url_has_allowed_host_and_scheme(
        url, allowed_hosts=allowed_domains, require_https=require_https
    )


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

    try:
        result, next_link = complete_login(request)
    except LoginError as exc:
        return HttpResponseBadRequest(str(exc)), None
    identity_user = result["id_token_claims"]

    # This should always be a liu email, but for reliability reasons no assumptions
    # are made thus try to search for liu-id with regex.
    preferred_username = identity_user.get("preferred_username", "")
    match = LIU_ID_REGEX.search(preferred_username)
    liu_id = match.group() if match else None

    if not liu_id:
        logger.warning(
            f"A LiU-ID could not be extracted when trying to login Entra ID user {preferred_username}"
        )
        return HttpResponseBadRequest("A LiU-ID could not be found."), None

    django_user, _ = get_or_create_user(liu_id)

    # Update fields from Entra ID
    me = get_me(result["access_token"])
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

    return HttpResponseRedirect(get_safe_redirect(request, next_link)), django_user


def auth_logout(request):
    logout(request=request)
    # Logout is local; the user's Entra session remains active.


def get_safe_redirect(request: HttpRequest, redirect_url=None):
    if redirect_url is None:
        redirect_url = request.GET.get(REDIRECT_FIELD_NAME, DEFAULT_REDIRECT)

    url_is_safe = is_safe_redirect_url(
        redirect_url, settings.ALLOWED_HOSTS, require_https=request.is_secure()
    )

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

        self.enforce_csrf(request)

        return self.get_user(validated_token), validated_token

    def enforce_csrf(self, request):
        # "Inspiration" taken from rest_framework.authentication.SessionAuthentication.enforce_csrf
        check = CsrfViewMiddleware(lambda req: None)

        reason = check.process_request(request)
        if reason:
            raise PermissionDenied(f"CSRF Failed: {reason}")
