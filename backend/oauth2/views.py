import logging

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .auth import (
    AUTH,
    SCOPES,
    auth_logout,
    external_auth_callback_login,
    get_safe_redirect,
)

logger = logging.getLogger(__name__)


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
        auth_logout(request)
        if response:
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")
            return response

        redirect_url = request.GET.get("next")
        if redirect_url:
            new_resp = HttpResponseRedirect(redirect_to=redirect_url)
        else:
            new_resp = HttpResponse(status=200)
        
        new_resp.delete_cookie("access_token")
        new_resp.delete_cookie("refresh_token")
        return new_resp 


class ExternalAuthCallbackView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        response, django_user = external_auth_callback_login(request)

        if django_user is None:
            return response

        # Admin page does not need access tokens, session based auth used for admin page.

        response = HttpResponseRedirect(redirect_to=response.url)

        response.set_cookie(
            "access_token",
            str(RefreshToken.for_user(django_user).access_token),
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="Lax",
        )

        response.set_cookie(
            "refresh_token",
            str(RefreshToken.for_user(django_user)),
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="Lax",
        )

        return response
