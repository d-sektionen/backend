from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect
from django.conf import settings
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import list_route, action
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken
import jwt

import datetime

from .serializers import UserSerializer
from .permissions import IsUser


@login_required
def generate_token(request):
    refresh = RefreshToken.for_user(request.user)

    if 'redirect' in request.GET:
        redirect_url = request.GET['redirect']
        querystring = 'access=' + str(refresh.access_token) + '&refresh=' + str(refresh)

        return redirect(redirect_url + ('&' if '?' in redirect_url else '?') + querystring)
    else:
        return JsonResponse({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

class UserViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (IsUser, ) # Add IsAdminUser too if you want, not really needed though 

    def get_object(self):
        return self.request.user if self.kwargs['pk'] == 'me' else super().get_object()

    @action(detail=False, methods=['get'])
    def identification_token(self, request):
        """
        Returns a jwt token, for identifying a user, NOT to be used for auth.

        Currently used to enable user identifying QR codes for the checkin app.
        (The QR codes are generated and read client side)
        """
        # TODO: implement reading of identification codes.
        expiry = datetime.datetime.utcnow() + datetime.timedelta(days=10)
        expiry = expiry.replace(second=0, microsecond=0, minute=0, hour=6)
        encoded = jwt.encode({'u': request.user.id, 'exp': expiry}, settings.SECRET_KEY, algorithm='HS256')

        return Response({'token': encoded, 'expires': str(expiry)}, status.HTTP_200_OK)

