from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import F
from rest_framework import viewsets, views, status
from rest_framework.response import Response

from account import kobra
from voting.models import Meeting, Attendant, Scanner, Vote, MadeVote, Alternative
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

    def create(self, request, *args, **kwargs):
        meeting_id = request.data['meeting']
        meeting = Meeting.objects.get(id=meeting_id)

        if 'card_id' in request.data:
            card_id = request.data['card_id']
            username = kobra.liu_id_from_card(card_id)
        elif 'username' in request.data:
            username = request.data['username'].strip().lower()
        else:
            return Response({'error': 'Missing required parameter username or card_id'}, status=status.HTTP_400_BAD_REQUEST)

        if username is None:
            return Response({'error': 'Unable to find student'}, status=status.HTTP_404_NOT_FOUND)

        user, created = User.objects.get_or_create(username=username)
        attendant, created = Attendant.objects.get_or_create(user=user, meeting=meeting)

        if created:
            return Response(AttendantSerializer(attendant).data, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Attendant already exist'}, status=status.HTTP_400_BAD_REQUEST)


class ScannerViewSet(viewsets.ModelViewSet):
    queryset = Scanner.objects.all()
    serializer_class = ScannerSerializer


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
