from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect
from django.conf import settings
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import list_route, action
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer, SimpleUserSerializer
from .permissions import IsUser
from .idtoken import generate_id_token, read_id_token


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

    @action(detail=False, methods=['get', 'post'])
    def identification_token(self, request):
        """
        Returns a jwt token, for identifying a user, NOT to be used for auth.

        Currently used to enable user identifying QR codes for the checkin app.
        (The QR codes are generated and read client side)
        """
        if request.method == 'GET':
            token = generate_id_token(request.user)
            return Response({'token': token}, status.HTTP_200_OK)
        elif request.method == 'POST':
            # TODO: validate that token param exists
            user = read_id_token(request.data['token'])
            return Response(SimpleUserSerializer(user).data, status.HTTP_200_OK)

        


