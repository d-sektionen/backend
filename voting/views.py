from django.db import transaction
from django.db.models import F, Q
from rest_framework import mixins, viewsets, status, serializers, exceptions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from django.shortcuts import get_object_or_404

from app.permissions import FixedDjangoModelPermissions
from account.permissions import AllowMembers
from .permissions import VotePermission, OpenAttendancePermission

from .models import Meeting, Attendant, Vote, MadeVote, Alternative, SpeakerRequest
from .serializers import (
    MeetingSerializer,
    MeetingAdminSerializer,
    SelfAttendSerializer,
    AttendantSerializer,
    VoteListSerializer,
    VoteDetailsSerializer,
    SpeakerRequestSerializer,
)


class NoDeleteViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    pass


class MeetingViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Meeting.objects.filter(archived=False)
    serializer_class = MeetingSerializer
    permission_classes = (AllowMembers,)

    def get_queryset(self):

        queryset = Meeting.objects.filter(archived=False).filter(
            Q(attendants__user=self.request.user) | Q(open_attendance=True)
        )
        return queryset


class MeetingAdminViewSet(NoDeleteViewSet):
    queryset = Meeting.objects.filter(archived=False)
    serializer_class = MeetingAdminSerializer
    permission_classes = (FixedDjangoModelPermissions,)


class SpeakerRequestView(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericAPIView,
):

    queryset = SpeakerRequest.objects.all()
    serializer_class = SpeakerRequestSerializer
    # TODO: Permission require user to be attendant?

    # TODO: Add error handling for missing meeting parameter.
    def get_queryset(self):
        queryset = SpeakerRequest.objects.all()
        queryset = queryset.filter(
            meeting_id=self.request.query_params.get("meeting_id", None)
        )
        queryset = queryset.order_by("-prioritized")
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_object(self):
        queryset = self.get_queryset()

        prioritized = "prioritized" in self.request.query_params
        obj = get_object_or_404(
            queryset, user=self.request.user, prioritized=prioritized
        )
        self.check_object_permissions(self.request, obj)
        return obj

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class SpeakerRequestDetailView(
    mixins.DestroyModelMixin, mixins.RetrieveModelMixin, GenericAPIView
):
    """
    Allows an admin to delete any SpeakerRequest.
    """

    queryset = SpeakerRequest.objects.all()
    serializer_class = SpeakerRequestSerializer
    permission_classes = (FixedDjangoModelPermissions,)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class SelfAttendView(mixins.CreateModelMixin, mixins.DestroyModelMixin, GenericAPIView):
    queryset = Attendant.objects.all()
    serializer_class = SelfAttendSerializer
    permission_classes = (OpenAttendancePermission,)

    def get_queryset(self):
        if "meeting_id" not in self.request.query_params:
            raise exceptions.ParseError(
                detail='Missing required parameter "meeting_id"'
            )
        meeting_id = self.request.query_params["meeting_id"]
        return Attendant.objects.filter(meeting_id=meeting_id)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_object(self):
        queryset = self.get_queryset()

        obj = get_object_or_404(queryset, user=self.request.user)
        self.check_object_permissions(self.request, obj)
        return obj

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class AttendantViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Attendant.objects.all()
    serializer_class = AttendantSerializer
    permission_classes = (FixedDjangoModelPermissions,)

    def get_queryset(self, meeting_specific=False):
        if self.request.method == "GET" or meeting_specific:
            if "meeting_id" not in self.request.query_params:
                raise exceptions.ParseError(
                    detail='Missing required parameter "meeting_id"'
                )
                # raise exceptions.ValidationError(
                #     detail='Missing required parameter "meeting_id"'
                # )
            meeting_id = self.request.query_params["meeting_id"]
            return Attendant.objects.filter(meeting_id=meeting_id)

        return Attendant.objects.all()

    @action(detail=False, methods=["delete"])
    def clear(self, request, pk=None):
        attendants = self.get_queryset(meeting_specific=True)
        attendants.delete()
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        if (
            "current" in request.query_params
            and request.query_params["current"] == "true"
        ):
            meetings = Meeting.objects.filter(attendants__user__in=[user])
            vote_ids = [x.id for x in filter(None, [x.current_vote for x in meetings])]
            votes = Vote.objects.filter(id__in=vote_ids).order_by("-id")
        elif user.has_perm("voting.view_vote"):
            # Show everything for an admin
            votes = Vote.objects.all()
        else:
            votes = Vote.objects.none()

        serializer = self.get_serializer(votes, many=True)
        return Response(serializer.data)


class MadeVoteViewSet(viewsets.ViewSet):
    @transaction.atomic  # Added to ensure that we don't end up with a plus-oned alternative but no existing record of it.
    def create(self, request):
        vote_id = request.data["vote_id"]
        alternative_id = request.data["alternative_id"]

        alternative = Alternative.objects.get(id=alternative_id)
        if str(alternative.vote_id) != str(vote_id):
            return Response(
                {"error": "Omröstningen hittades inte"},
                status=status.HTTP_404_NOT_FOUND,
            )

        vote = Vote.objects.get(id=vote_id)
        if not Attendant.objects.filter(
            meeting=vote.meeting, user=request.user
        ).exists():
            return Response(
                {"error": "Du måste närvara på mötet för att få rösta"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if MadeVote.objects.filter(vote_id=vote_id, user=request.user).exists():
            return Response(
                {"error": "Du har redan röstat i den här omröstningen"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Update the reference by performing the addition directly in the database (using reference F)
        alternative.num_votes = F("num_votes") + 1
        alternative.save()

        MadeVote.objects.create(vote_id=vote_id, user=request.user)

        return Response({"status": "ok"}, status=status.HTTP_200_OK)
