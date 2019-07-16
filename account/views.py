from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import list_route, action
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

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

