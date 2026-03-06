import logging

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.urls import reverse
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView as BaseTokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError

from datetime import datetime, timezone

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
        refresh_token = request.COOKIES.get("refresh_token")
        token = RefreshToken(refresh_token)
        token.blacklist()
    except Exception as e:
        logger.info(
            f"Blacklist did not recieve refresh token or some other error occurred: {e}"
        )
        return HttpResponseBadRequest()

    return None


class TokenRefreshView(BaseTokenRefreshView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            resp = Response({"error": "No refresh token"}, status=401)
            resp.delete_cookie("access_token")
            resp.delete_cookie("refresh_token", path=reverse("token_refresh"))
            return resp

        # Inject into request data so simplejwt can validate it and issue new tokens
        request.data["refresh"] = refresh_token

        try:
            response = super().post(request, *args, **kwargs)
        except TokenError as e:
            resp = Response({"error": str(e)}, status=401)
            resp.delete_cookie("access_token")
            resp.delete_cookie("refresh_token", path=reverse("token_refresh"))
            return resp

        if response.status_code == 200:
            new_access_token = AccessToken(response.data.get("access"))
            new_refresh_token = RefreshToken(response.data.get("refresh"))

            set_auth_cookies(response, new_access_token, new_refresh_token)

            del response.data["access"]
            del response.data["refresh"]

        return response


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
            response.delete_cookie("refresh_token", path=reverse("token_refresh"))
            return response

        redirect_url = request.GET.get("next")
        if redirect_url:
            new_resp = HttpResponseRedirect(redirect_to=redirect_url)
        else:
            new_resp = HttpResponse(status=200)

        new_resp.delete_cookie("access_token")
        new_resp.delete_cookie("refresh_token", path=reverse("token_refresh"))
        return new_resp


class ExternalAuthCallbackView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        response, django_user = external_auth_callback_login(request)

        if django_user is None:
            return response

        # Admin page does not need access tokens, session based auth used for admin page.

        response = HttpResponseRedirect(redirect_to=response.url)
        refresh_token = RefreshToken.for_user(django_user)

        set_auth_cookies(response, refresh_token.access_token, refresh_token)

        return response


def set_auth_cookies(response, access_token, refresh_token):
    refresh_token_exp = datetime.fromtimestamp(
        refresh_token.payload.get("exp"), tz=timezone.utc
    )
    access_token_exp = datetime.fromtimestamp(
        access_token.payload.get("exp"), tz=timezone.utc
    )

    response.set_cookie(
        "refresh_token",
        str(refresh_token),
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="Lax",
        path=reverse("token_refresh"),  # "/oauth2/login/refresh",
        expires=refresh_token_exp,
    )

    response.set_cookie(
        "access_token",
        str(access_token),
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="Lax",
        expires=access_token_exp,
    )
