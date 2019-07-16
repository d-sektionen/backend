from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import list_route
from rest_framework.response import Response

from rest_framework_jwt.settings import api_settings

from .serializers import UserSerializer
from .permissions import IsUser


@login_required
def generate_token(request):
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

    payload = jwt_payload_handler(request.user)
    token = jwt_encode_handler(payload)

    if 'redirect' in request.GET:
        redirect_url = request.GET['redirect']
        if '?' in redirect_url:
            redirect_url += '&token=' + token
        else:
            redirect_url += '?token=' + token

        return redirect(redirect_url)
    else:
        return JsonResponse({
            'token': token
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

    # def retrieve(self, request, *args, **kwargs):
    #     if kwargs['pk'] == 'me':
    #         serializer = self.get_serializer(request.user)
    #         return Response(serializer.data)
    #     else:
    #         return super(UserViewSet, self).retrieve(request, *args, **kwargs)

    # def update(self, request, *args, **kwargs):

    #     if kwargs['pk'] == 'me':
    #         instance = request.user
    #         serializer = self.serializer_class(instance, data=request.data, partial=True)
    #         serializer.is_valid(raise_exception=True)
    #         serializer.save()
    #         return Response(serializer.data)
    #     else:
    #         return super(UserViewSet, self).update(request, *args, **kwargs)

