from rest_framework import mixins, viewsets
from ..app.permissions import FixedDjangoModelPermissions
from .models import Occurrence
from .serializers import OccurrenceSerializer


# Create your views here.
class OccurrenceViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Occurrence.objects.filter(archived=False)
    serializer_class = OccurrenceSerializer
    permission_classes = (FixedDjangoModelPermissions,)
