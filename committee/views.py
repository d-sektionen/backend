from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from committee.serializers import CommitteeSerializer
from committee.models import Committee


@api_view(['GET'])
@permission_classes([AllowAny])
def get_committees(request: Request, format=None):
    committees = Committee.objects.all()
    return Response(
        CommitteeSerializer(committees, many=True).data,
        status.HTTP_200_OK
    )