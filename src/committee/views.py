from account.permissions import AllowMembers
from account.user import get_or_create_user
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from account.permissions import IsUser
from account.serializers import SimpleUserSerializer
from committee.serializers import CommitteeSerializer
from committee.models import Committee

from account.user import get_or_create_user
from .permissions import CommitteePermissions
from .serializers import CommitteeSerializer


class CommitteeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Committee.objects.all()
    serializer_class = CommitteeSerializer
    permission_classes = (AllowMembers,)

    @action(detail=False, methods=["post"], permission_classes=[CommitteePermissions])
    def set_committee_dependents(request: Request, format=None):
        """Set the dependents (ordförande & kassör) using data from Dsek-FetchR."""
        members = request.data

        for member in members:
            user, _ = get_or_create_user(member)
            committee = members[member]["Utskott"]
            committee_obj, _ = Committee.objects.get_or_create(name=committee)
            if committee_obj is not None:
                # Update committee
                committee_obj.members.add(user)
                committee_obj.save()

                # Update treasurer
                if members[member]["Kassör"] == "TRUE":
                    committee_obj.treasurer = user
                    if user.email != "":
                        committee_obj.treasurer_email = user.email

                # Update chairman
                elif members[member]["Ordförande"] == "TRUE":
                    committee_obj.chair = user
                    if user.email != "":
                        committee_obj.chair_email = user.email

                committee_obj.save()

            else:
                return Response(
                    {"error": "Det finns inget utskott med det ID:t"},
                    status.HTTP_400_BAD_REQUEST,
                )

        return Response({"ok": "Sektionsmedlemmar uppdaterade"}, status.HTTP_200_OK)
