import logging

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .auth import (
    AUTH,
    SCOPES,
    add_access_token_to_url,
    auth_logout,
    external_auth_callback_login,
    get_safe_redirect,
)

logger = logging.getLogger(__name__)


class RefreshView(TokenRefreshView):
    permission_classes = (IsAuthenticated,)


def blacklist_refresh_token(request):
    try:
        refresh_token = request.data.get("refresh")
        token = RefreshToken(refresh_token)
        token.blacklist()
    except Exception as e:
        logger.info(
            f"Blacklist did not recieve refresh token or some other error occurred: {e}"
        )
        return HttpResponseBadRequest()

    return None


class BlacklistView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        response = blacklist_refresh_token(request)
        if response:
            return response
        return HttpResponse(status=200)


class LoginView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        logger.debug(str(request))
        next_link = get_safe_redirect(request)
        logger.debug(f"Logging in user with redirect: {next_link}")
        # Save an http 302 by calling self.login(request) instead of redirect(self.login)
        return AUTH.login(
            request,
            next_link=next_link,
            scopes=SCOPES,
        )


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        response = blacklist_refresh_token(request)
        if response:
            return response

        return auth_logout(request=request)


class ExternalAuthCallbackView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        response, django_user = external_auth_callback_login(request)

        # Admin page does not need access tokens, session based auth used for admin page.
        redirect_url = add_access_token_to_url(url=response.url, user=django_user)

        response = HttpResponseRedirect(redirect_to=redirect_url)

        return response
