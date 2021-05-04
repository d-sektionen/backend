from django.shortcuts import render
from .models import LogEntry, LogStart
from rest_framework import viewsets, mixins
from .serializers import LogEntrySerializer, LogStartSerializer
from .permissions import LoggingPermissions


class LogEntryViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = LogEntrySerializer
    permission_classes = (LoggingPermissions,)
    queryset = LogEntry.objects.all()

    def get_queryset(self):
        return LogEntry.objects.filter(user=self.request.user)



class LogStartViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = LogStartSerializer
    permission_classes = (LoggingPermissions,)
    queryset = LogStart.objects.all()

    def get_queryset(self):
        return LogStart.objects.filter(user=self.request.user)



