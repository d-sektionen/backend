from account.permissions import AllowMembers
from rest_framework import viewsets

from .serializers import CommitteeMemberSerializer, CommitteeSerializer
from .models import Committee, CommitteeMember


class CommitteesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Committee.objects.all()
    serializer_class = CommitteeSerializer
    permission_classes = (AllowMembers,)


class CommitteeMembershipsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CommitteeMemberSerializer
    permission_classes = (AllowMembers,)

    def get_queryset(self):
        queryset = CommitteeMember.objects.filter(
            committee__id=self.kwargs.get("committee_id")
        )

        year = self.request.query_params.get("year")

        if year:
            queryset = queryset.filter(year=year)

        return queryset
