from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect
from django.conf import settings
from django_ical.views import ObjectDoesNotExist
from django.views.generic import TemplateView
from rest_framework import mixins, viewsets, status, exceptions
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt

from app.permissions import FixedDjangoModelPermissions
from django.contrib.auth import login, logout

import requests
import time
import jwt
import json

from .user import get_or_create_user

from .serializers import (
    MeSerializer,
    SimpleUserSerializer,
    InfomailUserSerializer,
    CalendarSubscriptionSerializer,
    PublicProfileSerializer,
    PrivateProfileSerializer,
)
from .idtoken import generate_id_token, read_id_token
from .models import CalendarSubscription, Profile
from account.adfs_token_validation import get_public_key


@login_required
def generate_token(request):
    refresh = RefreshToken.for_user(request.user)

    if "redirect" in request.GET:
        redirect_url = request.GET["redirect"]
        querystring = "access=" + str(refresh.access_token) + "&refresh=" + str(refresh)

        return redirect(
            redirect_url + ("&" if "?" in redirect_url else "?") + querystring
        )
    else:
        return JsonResponse(
            {"refresh": str(refresh), "access": str(refresh.access_token)}
        )


@csrf_exempt
def device_login(request):
    if len(request.body) == 0 or "device_code" not in request.body.decode("utf-8"):

        # user = User.objects.get(username__iexact="felli675")

        payload = {
            "client_id": settings.CLIENT_ID,
            "scope": "openid",
        }
        response = requests.post(
            "https://fs.liu.se/adfs/oauth2/devicecode",
            data=payload,
        )
        data = response.json()
        return JsonResponse(data)
    else:
        req = json.loads(request.body)
        device_code = req["device_code"]
        payload = {
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "client_id": settings.CLIENT_ID,
            "device_code": device_code,
        }

        # Poll for 5 seconds
        for _ in range(5):
            response = requests.post(
                "https://fs.liu.se/adfs/oauth2/token",
                data=payload,
            )
            if response.status_code == 200:
                data = response.json()
                id_token = data["id_token"]
                access_token = data["access_token"]
                public_key = get_public_key(
                    id_token, "https://fs.liu.se/adfs/discovery/keys"
                )
                decoded = jwt.decode(
                    id_token,
                    key=public_key,
                    algorithms=["RS256"],
                    audience=[settings.CLIENT_ID],
                )
                user = get_or_create_user(decoded["winaccountname"])[0]
                login(
                    request, user, backend="django.contrib.auth.backends.ModelBackend"
                )  # , backend=backend)

                decoded["access_token"] = access_token
                return JsonResponse(
                    {
                        "code": decoded,
                        "user": str(user),
                    }
                )
            time.sleep(1)
        return JsonResponse({"code": device_code})


def device_logout(request):

    logout(request)

    return JsonResponse({"user": str(request.user)})


class MeView(mixins.RetrieveModelMixin, GenericAPIView):
    serializer_class = MeSerializer
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


# Should be removed when a more suitable login view is implemented
class AdminLoginView(TemplateView):
    template_name = "admin.html"


class IdentificationTokenView(APIView):
    """
    Returns a jwt token, for identifying a user, NOT to be used for auth.

    Currently used to enable user identifying QR codes for the checkin app.
    (The QR codes are generated and read client side)

    """

    def get(self, request, *args, **kwargs):
        token = generate_id_token(request.user)
        return Response({"token": token}, status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        Verify a token (returns a user)

        example input:
        ```
        {
            "token": "string"
        }
        ```
        """
        try:
            user = read_id_token(request.data["token"])
        except ObjectDoesNotExist:
            raise exceptions.ParseError(detail="Token is invalid.")

        return Response(SimpleUserSerializer(user).data, status.HTTP_200_OK)


class InfomailSubscriberView(mixins.ListModelMixin, GenericAPIView):
    """
    Returns all users who are infomail subscribers.
    """

    permission_classes = [FixedDjangoModelPermissions]
    queryset = User.objects.filter(profile__infomail_subscriber=True)
    serializer_class = InfomailUserSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class InfomailEveryoneView(mixins.ListModelMixin, GenericAPIView):
    """
    Returns all users
    """

    permission_classes = [FixedDjangoModelPermissions]
    queryset = User.objects.all()
    serializer_class = InfomailUserSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ProfileView(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericAPIView):
    queryset = Profile.objects.all()
    serializer_class = PublicProfileSerializer

    def get(self, request, *args, **kwargs):
        if "pk" in kwargs:
            return self.retrieve(request, *args, **kwargs)
        else:
            return self.list(request, *args, **kwargs)


class MeProfileView(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericAPIView):
    serializer_class = PrivateProfileSerializer

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user).first()

    def get_object(self):
        return Profile.objects.filter(user=self.request.user).first()

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
class CalendarSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = CalendarSubscription.objects.all()
    serializer_class = CalendarSubscriptionSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return CalendarSubscription.objects.filter(user=self.request.user)
