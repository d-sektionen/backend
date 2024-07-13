from rest_framework.generics import GenericAPIView
from rest_framework import mixins
from django.shortcuts import get_object_or_404

from . import serializers
from .models import Request


class RequestView(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    GenericAPIView,
):
    """
    """

    queryset = Request.objects.all()
    serializer_class = serializers.RequestSerializer
    # TODO: permission only non member who is logged in

    def get_object(self):
        queryset = self.get_queryset()

        obj = get_object_or_404(queryset, username=self.request.user.username)
        self.check_object_permissions(self.request, obj)
        return obj

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
