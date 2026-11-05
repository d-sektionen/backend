from django.db import IntegrityError, transaction
from django.db.models import Exists, F, OuterRef, Q, ObjectDoesNotExist
from rest_framework import mixins, viewsets, status, exceptions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from django.shortcuts import get_object_or_404

from ..app.permissions import FixedDjangoModelPermissions
from ..account.permissions import AllowMembers
from .permissions import OpenAttendancePermission, SpeakerRequestPermission

from .models import Meeting, Attendant, Vote, MadeVote, Alternative, SpeakerRequest
from .casting import lock_choice, lock_eligibility
from . import memory_buffer
from .signals import batch_notifications, queue_alternative_update, _queue_event
from .serializers import (
    MeetingSerializer,
    MeetingAdminSerializer,
    SelfAttendSerializer,
    AttendantSerializer,
    VoteListSerializer,
    VoteDetailsSerializer,
    SpeakerRequestSerializer,
)

from ..membership.utils import student_member_liu_ids


def _with_meeting_reads(queryset, user):
    return queryset.annotate(
        _attending=Exists(
            Attendant.objects.filter(user=user, meeting_id=OuterRef("pk"))
        )
    )


def _with_vote_reads(queryset, user):
    return queryset.annotate(
        _has_voted=Exists(MadeVote.objects.filter(user=user, vote_id=OuterRef("pk")))
    ).prefetch_related("alternative_set")


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
        return _with_meeting_reads(
            Meeting.objects.filter(archived=False), self.request.user
        ).filter(Q(_attending=True) | Q(open_attendance=True))


class MeetingGuestViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Meeting.objects.filter(archived=False)
    serializer_class = MeetingSerializer
    # permission_classes = (AllowMembers,)

    def get_queryset(self):
        return _with_meeting_reads(
            Meeting.objects.filter(archived=False), self.request.user
        ).filter(_attending=True)


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
    queryset = SpeakerRequest.objects.select_related("user")
    serializer_class = SpeakerRequestSerializer
    permission_classes = (SpeakerRequestPermission,)
    # TODO: Permission require user to be attendant?

    # TODO: Require meeting to have speaker requests enabled.

    # TODO: Add error handling for missing meeting parameter.
    def get_queryset(self):
        queryset = self.queryset.all()
        queryset = queryset.filter(
            meeting_id=self.request.query_params.get("meeting_id", None)
        )
        queryset = queryset.order_by("-prioritized", "id")
        return queryset

    def perform_create(self, serializer: SpeakerRequestSerializer):
        SpeakerRequest.objects.get_or_create(
            user=self.request.user,
            meeting=serializer.validated_data["meeting"],
            prioritized=serializer.validated_data.get("prioritized", False),
        )

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

    queryset = SpeakerRequest.objects.select_related("user")
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
        try:
            # The unique constraint also handles simultaneous check-in retries.
            with transaction.atomic():
                serializer.save(user=self.request.user)
        except IntegrityError:
            if Attendant.objects.filter(
                user=self.request.user, meeting=serializer.validated_data["meeting"]
            ).exists():
                raise exceptions.ValidationError(
                    "You are already attending this meeting"
                )
            raise
        # The serializer's nested meeting belongs to this newly created attendee.
        # Reuse that request-local fact without another attendance SELECT.
        serializer.instance.meeting._attending = True

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
            return Attendant.objects.filter(meeting_id=meeting_id).select_related(
                "user", "meeting"
            )

        return Attendant.objects.all()

    @action(detail=False, methods=["delete"])
    def clear(self, request, pk=None):
        attendants = self.get_queryset(meeting_specific=True)
        # Keep the existing membership criterion, including guests whose rights
        # flag differs from their current membership. Signals still fire per row.
        with batch_notifications():
            attendants.filter(user__username__in=student_member_liu_ids()).delete()

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
            return _with_vote_reads(
                Vote.objects.filter(meeting_id=meeting_id, open=True), user
            )
        return Vote.objects.none()


class VoteAdminViewSet(viewsets.ModelViewSet):
    serializer_class = VoteListSerializer
    queryset = Vote.objects.all()
    permission_classes = (FixedDjangoModelPermissions,)

    def perform_create(self, serializer):
        with transaction.atomic():
            meeting = Meeting.objects.select_for_update().get(
                pk=serializer.validated_data["meeting"].pk
            )
            if meeting.current_vote_id and Vote.objects.filter(
                pk=meeting.current_vote_id, open=True
            ).exists():
                raise exceptions.ValidationError(
                    "Close or discard the current ballot before opening another."
                )
            vote = serializer.save()
            if vote.open:
                memory_buffer.initialize(vote.pk)

    def update(self, request, *args, **kwargs):
        # This prototype supports closing only; changing alternatives or
        # reopening a ballot would invalidate the in-memory snapshot.
        data = request.data
        if data.get("open") is not False or set(data) - {
            "open", "question", "meeting", "alternatives"
        }:
            raise exceptions.ValidationError("Only closing a ballot is supported by the voting prototype.")

        vote = self.get_object()
        with transaction.atomic():
            vote = Vote.objects.select_for_update().get(pk=vote.pk)
            if ("question" in data and data["question"] != vote.question) or (
                "meeting" in data and str(data["meeting"]) != str(vote.meeting_id)
            ):
                raise exceptions.ValidationError("Ballot edits are not supported by the voting prototype.")
            if "alternatives" in data:
                supplied = data["alternatives"]
                if not isinstance(supplied, list) or any(
                    not isinstance(item, dict)
                    or not isinstance(item.get("id"), (int, str))
                    or not isinstance(item.get("text"), str)
                    for item in supplied
                ):
                    raise exceptions.ValidationError("Ballot edits are not supported by the voting prototype.")
                supplied_choices = sorted((str(item["id"]), item["text"]) for item in supplied)
                current_choices = sorted(
                    (str(pk), text) for pk, text in Alternative.objects.filter(vote=vote).values_list("pk", "text")
                )
                if supplied_choices != current_choices:
                    raise exceptions.ValidationError("Ballot edits are not supported by the voting prototype.")
            if vote.open:
                # Keep a failed close frozen until retry: a lost DB connection
                # can leave the commit outcome uncertain.
                memory_buffer.freeze(vote.pk)
                voters, counts = memory_buffer.snapshot(vote.pk)
                alternatives = set(Alternative.objects.filter(vote=vote).values_list("pk", flat=True))
                if not set(counts).issubset(alternatives) or sum(counts.values()) != len(voters):
                    raise memory_buffer.BufferUnavailable("Invalid buffer; discard ballot and revote.")
                MadeVote.objects.bulk_create(
                    [MadeVote(user_id=user_id, vote_id=vote.pk) for user_id in voters],
                    batch_size=500,
                )
                for alternative_id, count in counts.items():
                    Alternative.objects.filter(pk=alternative_id, vote=vote).update(
                        num_votes=F("num_votes") + count
                    )
                Vote.objects.filter(pk=vote.pk).update(open=False)
                vote.open = False
                transaction.on_commit(lambda: memory_buffer.discard(vote.pk))
                _queue_event("delete_vote", {"id": vote.pk, "meeting": vote.meeting_id},
                             f"meeting_votes_{vote.meeting_id}")
        return Response(self.get_serializer(vote).data)

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "list":
            # The browser uses event_id; meeting_id is the voting API spelling.
            # Unfiltered lists retain the existing all-meetings history contract.
            for parameter in ("event_id", "meeting_id"):
                value = self.request.query_params.get(parameter)
                if value is not None:
                    try:
                        meeting_id = int(value)
                    except (ValueError, TypeError):
                        raise exceptions.ParseError(f'Invalid "{parameter}"')
                    queryset = queryset.filter(meeting_id=meeting_id)
        if self.action in ("list", "retrieve"):
            return _with_vote_reads(queryset, self.request.user)
        return queryset

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
            vote_ids = list(vote.values_list("pk", flat=True))
            vote.delete()
            for vote_id in vote_ids:
                transaction.on_commit(lambda vote_id=vote_id: memory_buffer.discard(vote_id))

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
            alternative = lock_choice(alternative_id)
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

        if not lock_eligibility(alternative.meeting_id, request.user):
            return Response(
                {"error": "Du måste närvara på mötet för att få rösta"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Make sure that no one can make a vote after the meeting's voting admins have set the Vote to inactive:
        if alternative.current_vote_id != vote_id or not alternative.open:
            return Response(
                {"error": "Den här omröstningen är inte aktiv"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not memory_buffer.cast(vote_id, request.user.pk, alternative.id):
            return Response(
                {"error": "Du har redan röstat i den här omröstningen"},
                status=status.HTTP_403_FORBIDDEN,
            )

        queue_alternative_update(
            alternative.id, alternative.text, vote_id, alternative.meeting_id
        )

        return Response({"status": "ok"}, status=status.HTTP_200_OK)
