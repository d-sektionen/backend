from django.db import transaction
from django.db.models import F, Q
from rest_framework import mixins, viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from app.permissions import FixedDjangoModelPermissions
from .permissions import VotePermission

from .models import Meeting, Attendant, Vote, MadeVote, Alternative
from .serializers import MeetingSerializer, AttendantSerializer, VoteListSerializer, VoteDetailsSerializer

class NoDeleteViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    pass

class MeetingViewSet(NoDeleteViewSet):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    permission_classes = (FixedDjangoModelPermissions,) 

class AttendantViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Attendant.objects.all()
    serializer_class = AttendantSerializer
    permission_classes = (FixedDjangoModelPermissions,)

    def get_queryset(self):
        if 'meeting' not in self.request.query_params:
            raise ValidationError(detail='Missing required parameter "meeting"')

        meeting_id = self.request.query_params['meeting']
        meeting = Meeting.objects.get(id=meeting_id)

        return meeting.attendant_set

class VoteViewSet(NoDeleteViewSet):
    serializer_class = VoteListSerializer
    queryset = Vote.objects.all()
    permission_classes = (VotePermission,)

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = VoteDetailsSerializer
        return super(VoteViewSet, self).retrieve(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        This solution is very ugly but makes sure that we return a QuerySet. This
        is needed for the retrieval of individual vote objects to work correctly.

        It might be better to replace this with a raw SQL query.
        """

        user = self.request.user
        if 'current' in request.query_params and request.query_params['current'] == 'true':
            meetings = Meeting.objects.filter(attendant__user__in=[user])
            vote_ids = [x.id for x in filter(None, [x.current_vote for x in meetings])]
            votes = Vote.objects.filter(id__in=vote_ids).order_by('-id')
        elif user.has_perm('voting.view_vote'):
            # Show everything for an admin
            votes = Vote.objects.all()
        else:
            votes = Vote.objects.none()

        serializer = self.get_serializer(votes, many=True)
        return Response(serializer.data)


class MadeVoteViewSet(viewsets.ViewSet):
    @transaction.atomic  # Added to ensure that we don't end up with a plus-oned alternative but no existing record of it.
    def create(self, request):
        vote_id = request.data['vote_id']
        alternative_id = request.data['alternative_id']

        alternative = Alternative.objects.get(id=alternative_id)
        if str(alternative.vote_id) != str(vote_id):
            return Response({'error': 'Omröstningen hittades inte'}, status=status.HTTP_404_NOT_FOUND)

        vote = Vote.objects.get(id=vote_id)
        if not Attendant.objects.filter(meeting=vote.meeting, user=request.user).exists():
            return Response({'error': 'Du måste närvara på mötet för att få rösta'}, status=status.HTTP_403_FORBIDDEN)

        if MadeVote.objects.filter(vote_id=vote_id, user=request.user).exists():
            return Response({'error': 'Du har redan röstat i den här omröstningen'}, status=status.HTTP_403_FORBIDDEN)


        # Update the reference by performing the addition directly in the database (using reference F)
        alternative.num_votes = F('num_votes') + 1
        alternative.save()

        MadeVote.objects.create(vote_id=vote_id, user=request.user)

        return Response({'status': 'ok'}, status=status.HTTP_200_OK)
