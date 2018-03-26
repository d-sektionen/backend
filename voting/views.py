from django.db import transaction
from django.db.models import F, Q
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from voting.permissions import AdminMeetingPermission, ScannerOrAdminMeetingPermission

from voting.models import Meeting, Attendant, Scanner, Vote, MadeVote, Alternative
from voting.serializers import MeetingSerializer, AttendantSerializer, ScannerSerializer, VoteListSerializer, VoteDetailsSerializer, MeetingReadSerializer
from voting.view_helpers import different_read_serializer, UserIdentifiableViewSet


@different_read_serializer
class MeetingViewSet(viewsets.ModelViewSet):
    serializer_class = MeetingSerializer
    read_serializer_class = MeetingReadSerializer
    permission_classes = (AdminMeetingPermission,)

    def get_queryset(self):
        user = self.request.user
        user_groups = user.groups.all()
        meetings = Meeting.objects.filter(section__admin_group__in=user_groups)

        return meetings


class AttendantViewSet(UserIdentifiableViewSet):
    queryset = Attendant.objects.all()
    serializer_class = AttendantSerializer
    check_section_membership = True
    permission_classes = (AdminMeetingPermission, ScannerOrAdminMeetingPermission)


    def get_queryset(self):
        if 'meeting' not in self.request.query_params:
            raise ValidationError(detail='Missing required parameter "meeting"')

        meeting_id = self.request.query_params['meeting']
        meeting = Meeting.objects.get(id=meeting_id)

        return meeting.attendant_set


class ScannerViewSet(UserIdentifiableViewSet):
    queryset = Scanner.objects.all()
    serializer_class = ScannerSerializer
    permission_classes = (AdminMeetingPermission,)


    def get_queryset(self):
        if 'meeting' in self.request.query_params:
            meeting_id = self.request.query_params['meeting']
            meeting = Meeting.objects.get(id=meeting_id)

            return meeting.scanner_set
        else:
            return Scanner.objects.filter(user=self.request.user)


class VoteViewSet(viewsets.ModelViewSet):
    serializer_class = VoteListSerializer
    queryset = Vote.objects.all()
    permission_classes = (AdminMeetingPermission,)

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
        user_groups = user.groups.all()
        if 'current' in request.query_params and request.query_params['current'] == 'true':
            meetings = Meeting.objects.filter(attendant__user__in=[user]).order_by('-id')
        else:
            meetings = Meeting.objects.filter(section__admin_group__in=user_groups)

        vote_ids = [x.id for x in filter(None, [x.current_vote for x in meetings])]
        votes = Vote.objects.filter(id__in=vote_ids)

        serializer = self.get_serializer(votes, many=True)
        return Response(serializer.data)


class MadeVoteViewSet(viewsets.ViewSet):
    @transaction.atomic  # Added to ensure that we don't end up with a plus-oned alternative but no existing record of it.
    def create(self, request):
        vote_id = request.data['vote_id']
        alternative_id = request.data['alternative_id']

        if MadeVote.objects.filter(vote_id=vote_id, user=request.user).exists():
            return Response({'error': 'Du har redan röstat i den här omröstningen'}, status=status.HTTP_403_FORBIDDEN)

        alternative = Alternative.objects.get(id=alternative_id)
        if str(alternative.vote_id) != str(vote_id):
            return Response({'error': 'Omröstningen hittades inte'}, status=status.HTTP_404_NOT_FOUND)

        # Update the reference by performing the addition directly in the database (using reference F)
        alternative.num_votes = F('num_votes') + 1
        alternative.save()

        MadeVote.objects.create(vote_id=vote_id, user=request.user)

        return Response({'status': 'ok'}, status=status.HTTP_200_OK)
