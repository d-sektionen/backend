from rest_framework import viewsets

from voting.models import Meeting, Attendant, Scanner, Vote, MadeVote
from voting.serializers import MeetingSerializer, AttendantSerializer, ScannerSerializer, VoteSerializer, MadeVoteSerializer


class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer


class AttendantViewSet(viewsets.ModelViewSet):
    queryset = Attendant.objects.all()
    serializer_class = AttendantSerializer


class ScannerViewSet(viewsets.ModelViewSet):
    queryset = Scanner.objects.all()
    serializer_class = ScannerSerializer


class VoteViewSet(viewsets.ModelViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer


class MadeVoteViewSet(viewsets.ModelViewSet):
    queryset = MadeVote.objects.all()
    serializer_class = MadeVoteSerializer

