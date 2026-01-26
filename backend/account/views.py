from django.contrib.auth.models import User
from django_ical.views import ObjectDoesNotExist
from rest_framework import exceptions, mixins, status, viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from ..app.permissions import FixedDjangoModelPermissions
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


class MeView(mixins.RetrieveModelMixin, GenericAPIView):
    serializer_class = MeSerializer
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


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
