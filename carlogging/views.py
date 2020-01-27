from django.shortcuts import render
from .models import Logg
from rest_framework import viewsets, mixins
from .serializers import LoggSerializer


class LoggingViewSet(
    mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
    ):
    serializer_class = LoggSerializer
    queryset = Logg.objects.all()
    
    def get_queryset(self):
        return Logg.objects.all()
    