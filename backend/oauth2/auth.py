import logging
import re
import urllib.parse as urlparse

from account.user import get_or_create_user
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME, login, logout
from django.contrib.auth.models import User, update_last_login
from django.http import HttpRequest, HttpResponseRedirect
from django.utils.encoding import iri_to_uri
from django.utils.http import url_has_allowed_host_and_scheme
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

logger = logging.getLogger(__name__)

AUTH = settings.MICROSOFT_IDENTITY
ALLOWED_HOSTS = settings.ALLOWED_HOSTS
SCOPES = ["User.Read"]
LIU_ID_REGEX = re.compile(r"[a-z]{4,5}[0-9]{2,3}")
DEFAULT_REDIRECT = "/"


def external_auth_callback_login(request):
    if request.user.is_authenticated:
        logging.debug(f"Reauthenticating user: {request.user}\n")

    response = AUTH.auth_response(request)

    if not isinstance(response, HttpResponseRedirect):
        logger.warning("Auth error occurred at Entra ID endpoint")
        return response

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
        return response

    django_user, _ = get_or_create_user(liu_id)
    login(request, django_user, backend="django.contrib.auth.backends.ModelBackend")
    update_last_login(None, django_user)
    logger.debug(f"Django user login: {django_user}")

    return response, django_user


def auth_logout(request):
    logout(request=request)
    return AUTH.logout(request)


def get_safe_redirect(request: HttpRequest):
    path = request.get_full_path()

    redirect_url = request.GET.get(REDIRECT_FIELD_NAME, path)
    logger.debug(f"redirect_url: {redirect_url}")

    url_is_safe = url_has_allowed_host_and_scheme(
        url=redirect_url,
        allowed_hosts=ALLOWED_HOSTS,
        require_https=False,
    )

    logger.debug(f"Safe redirect: {url_is_safe} ({redirect_url})")

    return iri_to_uri(redirect_url) if url_is_safe else DEFAULT_REDIRECT


def add_access_token_to_url(url: str, user: User):
    url_parts = urlparse.urlparse(url)
    parsed_query = dict(urlparse.parse_qsl(url_parts.query))

    access = AccessToken.for_user(user=user)
    refresh = RefreshToken.for_user(user=user)
    params = {"access": str(access), "refresh": str(refresh)}
    params.update(parsed_query)

    url_parts_with_tokens = url_parts._replace(query=urlparse.urlencode(params))
    final_url = urlparse.urlunparse(url_parts_with_tokens)

    return final_url
