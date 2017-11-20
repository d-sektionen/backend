from rest_framework import viewsets

from voting.models import Meeting, Attendant, Scanner, Vote, MadeVote
from voting.serializers import MeetingSerializer, AttendantSerializer, ScannerSerializer, VoteListSerializer, MadeVoteSerializer, VoteDetailsSerializer


class MeetingViewSet(viewsets.ModelViewSet):
    serializer_class = MeetingSerializer

    def get_queryset(self):
        user = self.request.user
        user_groups = user.groups.all()
        meetings = Meeting.objects.filter(section__admin_group__in=user_groups)

        return meetings


class AttendantViewSet(viewsets.ModelViewSet):
    queryset = Attendant.objects.all()
    serializer_class = AttendantSerializer


class ScannerViewSet(viewsets.ModelViewSet):
    queryset = Scanner.objects.all()
    serializer_class = ScannerSerializer


class VoteViewSet(viewsets.ModelViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteListSerializer

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = VoteDetailsSerializer
        return super(VoteViewSet, self).retrieve(request, *args, **kwargs)


class MadeVoteViewSet(viewsets.ModelViewSet):
    queryset = MadeVote.objects.all()
    serializer_class = MadeVoteSerializer

