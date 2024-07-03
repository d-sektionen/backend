from django.db import transaction
from django.db.models import F, Q, ObjectDoesNotExist
from rest_framework import mixins, viewsets, status, exceptions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from django.shortcuts import get_object_or_404

from app.permissions import FixedDjangoModelPermissions
from account.permissions import AllowMembers
from .permissions import OpenAttendancePermission, SpeakerRequestPermission

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

from membership.utils import check_membership


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
        queryset = (
            Meeting.objects.filter(archived=False)
            .filter(Q(attendants__user=self.request.user) | Q(open_attendance=True))
            .distinct()
        )
        return queryset


class MeetingGuestViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Meeting.objects.filter(archived=False)
    serializer_class = MeetingSerializer
    # permission_classes = (AllowMembers,)

    def get_queryset(self):
        queryset = Meeting.objects.filter(archived=False).filter(
            Q(attendants__user=self.request.user)
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
    permission_classes = (SpeakerRequestPermission,)
    # TODO: Permission require user to be attendant?

    # TODO: Require meeting to have speaker requests enabled.

    # TODO: Add error handling for missing meeting parameter.
    def get_queryset(self):
        queryset = SpeakerRequest.objects.all()
        queryset = queryset.filter(
            meeting_id=self.request.query_params.get("meeting_id", None)
        )
        queryset = queryset.order_by("-prioritized", "id")
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

    # OBS: hantera i denna så att en person som inte har
    # voting rights inte räknas in här. Den ska istället räknas
    # till guests eller liknande...

    # denna kanske kan innehålla member_attendants och
    # guest_attendants som skickas till frontenden
    # genom att serializern separerar dem i två olika
    # dictionaries...?

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

        for attendant in attendants:
            # do not remove guests from meeting:
            if check_membership(attendant.user.username):
                attendant.delete()

        # attendants.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class VoteViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = VoteListSerializer
    queryset = Vote.objects.all()

    def get_queryset(self):
        user = self.request.user
        if "meeting_id" not in self.request.query_params:
            raise exceptions.ParseError(
                detail='Missing required parameter "meeting_id"'
            )
        meeting_id = self.request.query_params["meeting_id"]
        if Meeting.objects.filter(id=meeting_id, attendants__user__in=[user]).exists():
            return Vote.objects.filter(meeting_id=meeting_id, open=True)
        return Vote.objects.none()


class VoteAdminViewSet(viewsets.ModelViewSet):
    serializer_class = VoteListSerializer
    queryset = Vote.objects.all()
    permission_classes = (FixedDjangoModelPermissions,)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return VoteDetailsSerializer
        return VoteListSerializer

    def destroy(self, request, pk=None):
        if "meeting_id" not in request.query_params:
            raise exceptions.ParseError(
                detail='Missing required parameter "meeting_id"'
            )

        if "vote_id" not in request.query_params:
            raise exceptions.ParseError(detail='Missing required parameter "vote_id"')

        vote = Vote.objects.filter(
            id=request.query_params["vote_id"],
            meeting_id=request.query_params["meeting_id"],
        )
        if vote:
            vote.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class MadeVoteViewSet(viewsets.ViewSet):
    permission_classes = (AllowMembers,)

    # Added to ensure that we don't end up with a plus-oned alternative but no existing record of it:
    @transaction.atomic
    def create(self, request):
        if "vote_id" not in request.data:
            raise exceptions.ParseError(detail='Missing required parameter "vote_id"')

        if "alternative_id" not in request.data:
            raise exceptions.ParseError(
                detail='Missing required parameter "alternative_id"'
            )
        vote_id = request.data["vote_id"]
        alternative_id = request.data["alternative_id"]

        try:
            alternative = Alternative.objects.get(id=alternative_id)
        except ObjectDoesNotExist:
            return Response(
                {
                    "error": "Alternativet hittades inte. Omröstningen kan ha tagits bort"
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if alternative.vote_id != vote_id:
            return Response(
                {"error": "Alternativet hör inte till omröstningen"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            vote = Vote.objects.get(id=vote_id)
        except ObjectDoesNotExist:
            return Response(
                {"error": "Omröstningen hittades inte"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not Attendant.objects.filter(
            meeting=vote.meeting, user=request.user
        ).exists():
            return Response(
                {"error": "Du måste närvara på mötet för att få rösta"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Make sure that no one can make a vote after the meeting's voting admins have set the Vote to inactive:
        if (
            vote.meeting.current_vote.id != vote.id
            or not vote.meeting.current_vote.open
        ):
            return Response(
                {"error": "Den här omröstningen är inte aktiv"},
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
