from rest_framework import mixins, viewsets
from rest_framework.generics import GenericAPIView

from ..app.permissions import FixedDjangoModelPermissions
from ..account.permissions import AllowMembers

from .models import LogEntry, Key
from .serializers import KeySerializer, LogEntrySerializer


class KeyView(
    mixins.ListModelMixin,
    GenericAPIView,
):
    queryset = Key.objects.all()
    serializer_class = KeySerializer
    permission_classes = (AllowMembers,)

    def get_queryset(self):
        queryset = Key.objects.all()
        queryset = queryset.order_by("order")
        return queryset

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class LogEntryViewSet(
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = LogEntry.objects.all()
    serializer_class = LogEntrySerializer
    permission_classes = (FixedDjangoModelPermissions,)
