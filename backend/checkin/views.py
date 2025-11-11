from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework import mixins, viewsets, status


from . import serializers
from .models import EventBase, Doorkeeper
from .permissions import OnlyDoorkeepersRegister, DoorkeeperPermission


class DoorkeeperViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Doorkeeper.objects.all()
    serializer_class = serializers.DoorkeeperSerializer
    permission_classes = (DoorkeeperPermission,)

    def get_queryset(self):
        if "event_id" in self.request.query_params:
            event_id = self.request.query_params["event_id"]

            return Doorkeeper.objects.filter(event_id=event_id)
        else:
            # Returns Doorkeepers for all events if no event is specified,
            # maybe it should be limited to event types the User is admin for.
            return Doorkeeper.objects.all()


class EventBaseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Events where the user is a doorkeeper items to be viewed.
    """

    queryset = EventBase.objects.all().select_subclasses()
    serializer_class = serializers.EventBaseSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset

        queryset = queryset.filter(doorkeeper__user__pk=user.pk).filter(archived=False)
        return queryset


class RegisterView(GenericAPIView):
    """
    View with only POST for Doorkeepers to do an action for users to an EventBase.
    """

    serializer_class = serializers.RegisterSerializer
    permission_classes = (OnlyDoorkeepersRegister,)

    def post(self, request, *args, **kwargs):
        serializer = serializers.RegisterSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "detail": 'Validation of fields "'
                    + ", ".join(serializer.errors.keys())
                    + '" failed.',
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = serializer.validated_data["user"]

        if user is None:
            return Response(
                {"detail": "User not found."}, status=status.HTTP_400_BAD_REQUEST
            )

        action = serializer.data["action"]
        event = EventBase.objects.get_subclass(pk=serializer.data["event"])

        return event.on_register(
            user, action
        )  # Response(event.name, status=status.HTTP_200_OK)
