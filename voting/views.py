from rest_framework import viewsets

from voting.models import Section
from voting.serializers import SectionSerializer


class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
