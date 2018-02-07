from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import F
from rest_framework import viewsets, views, status
from rest_framework.decorators import list_route
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from account import kobra
from voting.decorators import extract_user, extract_username
from voting.models import Meeting, Attendant, Scanner, Vote, MadeVote, Alternative
from voting.serializers import MeetingSerializer, AttendantSerializer, ScannerSerializer, VoteListSerializer, MadeVoteSerializer, VoteDetailsSerializer


class MeetingViewSet(viewsets.ModelViewSet):
    serializer_class = MeetingSerializer

    def get_queryset(self):
        user = self.request.user
        user_groups = user.groups.all()
        meetings = Meeting.objects.filter(section__admin_group__in=user_groups)

        return meetings


class UserIdentifiableViewSet(viewsets.ModelViewSet):
    def get_model(self):
        return self.serializer_class.Meta.model

    @extract_user
    def create(self, request, *args, **kwargs):
        meeting_id = request.data['meeting']
        meeting = Meeting.objects.get(id=meeting_id)
        user = kwargs['user']

        # TODO: Verify section membership
        attendant, created = self.get_model().objects.get_or_create(user=user, meeting=meeting)

        if created:
            return Response(self.serializer_class(attendant).data, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': self.get_model().__name__ + ' already exist'}, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['delete'], url_path='')
    @extract_username
    def delete(self, request, *args, **kwargs):
        meeting_id = request.data['meeting']
        meeting = Meeting.objects.get(id=meeting_id)
        username = kwargs['username']

        attendant = self.get_model().objects.filter(user__username=username, meeting=meeting).first()
        if attendant is not None:
            attendant.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': self.get_model().__name__ + ' does not exist'}, status=status.HTTP_400_BAD_REQUEST)


class AttendantViewSet(UserIdentifiableViewSet):
    queryset = Attendant.objects.all()
    serializer_class = AttendantSerializer

    def get_queryset(self):
        if 'meeting' not in self.request.query_params:
            raise ValidationError(detail='Missing required parameter "meeting"')

        meeting_id = self.request.query_params['meeting']
        meeting = Meeting.objects.get(id=meeting_id)

        return meeting.attendant_set


class ScannerViewSet(UserIdentifiableViewSet):
    queryset = Scanner.objects.all()
    serializer_class = ScannerSerializer

    def get_queryset(self):
        if 'meeting' in self.request.query_params:
            meeting_id = self.request.query_params['meeting']
            meeting = Meeting.objects.get(id=meeting_id)

            return meeting.scanner_set
        else:
            return Scanner.objects.filter(user=self.request.user)


class VoteViewSet(viewsets.ModelViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteListSerializer

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = VoteDetailsSerializer
        return super(VoteViewSet, self).retrieve(request, *args, **kwargs)


class MadeVoteViewSet(viewsets.ViewSet):
    @transaction.atomic  # Added to ensure that we don't end up with a plus-oned alternative but no existing record of it.
    def create(self, request):
        vote_id = request.data['vote_id']
        alternative_id = request.data['alternative_id']

        if MadeVote.objects.filter(vote_id=vote_id, user=request.user).exists():
            return Response({'error': 'Vote has already been made'}, status=status.HTTP_403_FORBIDDEN)

        alernative = Alternative.objects.get(id=alternative_id)
        if str(alernative.vote_id) != str(vote_id):
            return Response({'error': 'Unable to find vote'}, status=status.HTTP_404_NOT_FOUND)

        alernative.num_votes = F('num_votes') + 1
        alernative.save()

        MadeVote.objects.create(vote_id=vote_id, user=request.user)

        return Response(status=status.HTTP_204_NO_CONTENT)
