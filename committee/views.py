from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response

from account.permissions import IsUser
from account.serializers import SimpleUserSerializer
from committee.serializers import CommitteeSerializer
from committee.models import Committee

from membership.utils import check_membership
from account.user import get_or_create_user

@api_view(['GET'])
@permission_classes([IsUser])
def get_committees(request: Request, format=None):
    """Returns a list of all committees, along with their contacts."""
    committees = Committee.objects.all()
    return Response(
        CommitteeSerializer(committees, many=True).data,
        status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([IsUser])
def get_committee(request: Request, id: int, format=None):
    """Returns the specified committee, along with its contact."""
    committee = Committee.objects.filter(id=id).first()
    if committee is None:
        return Response(
            {'error': 'Det finns inget utskott med det ID:t'},
            status.HTTP_404_NOT_FOUND
        )
    return Response(
        CommitteeSerializer(committee).data,
        status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([IsUser])
def get_committee_members(request: Request, id: int, format=None):
    """Returns a list of members for the specifed committee."""
    committee = Committee.objects.filter(id=id).first()
    if committee is None:
        return Response(
            {'error': 'Det finns inget utskott med det ID:t'},
            status.HTTP_404_NOT_FOUND
        )
    return Response(
        SimpleUserSerializer(committee.members, many=True).data,
        status.HTTP_200_OK
    )

@api_view(['POST'])
@permission_classes([IsUser])
def set_commite_dependents(request: Request, format=None):
    """Set the dependents (ordförande & kassör) using data from Dsek-FetchR."""
    members = request.data

    for member in members:
        user,_ = get_or_create_user(member)
        committee = members[member]['Utskott']
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
            {'error': 'Det finns inget utskott med det ID:t'},
            status.HTTP_400_BAD_REQUEST
        )

    return Response(
        {'ok': 'Sektionsmedlemmar uppdaterade'},
        status.HTTP_200_OK
    )