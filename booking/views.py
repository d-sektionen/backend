from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from app.permissions import FixedDjangoModelPermissions
from .models import Booking, Item
from .serializers import BookingSerializer, ItemSerializer
from .permissions import BookingPermissions


class BookingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows bookings to be viewed, created, edited or deleted.
    """

    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = (BookingPermissions,)

    def get_queryset(self):
        queryset = Booking.objects.all()
        item = self.request.query_params.get("item", None)
        future = self.request.query_params.get("future", None)
        user = self.request.query_params.get("user", None)
        confirmed = self.request.query_params.get("confirmed", None)
        restricted_timeslot = self.request.query_params.get("restricted_timeslot", None)
        after = self.request.query_params.get("after", None)
        before = self.request.query_params.get("before", None)

        if user == "me":
            user = self.request.user.id

        if item:
            queryset = queryset.filter(item=item)
        if future != None:
            queryset = queryset.filter(end__gt=timezone.now())
        if after != None:
            queryset = queryset.filter(start__gt=after)
        if before != None:
            queryset = queryset.filter(end__lt=before)
        if user:
            queryset = queryset.filter(user=user)
        if confirmed:
            queryset = queryset.filter(confirmed=confirmed)
        if restricted_timeslot:
            queryset = queryset.filter(restricted_timeslot=restricted_timeslot)
        return queryset

    @action(
        detail=True, methods=["put"], permission_classes=[FixedDjangoModelPermissions],
    )
    def confirm(self, request, pk=None):
        booking = self.get_object()
        booking.confirmed = True
        booking.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def should_auto_confirm(self, data, exists=False):
        # If booking is a normal booking.
        if not data["restricted_timeslot"]:
            queryset = Booking.objects.all()

            # on update don't compare with self.
            if exists:
                queryset = queryset.exclude(pk=self.get_object().id)

            # If no confirmed restricted timeslot is overlapping with booking, auto confirm.
            queryset = Booking.objects.filter(
                restricted_timeslot=True,
                confirmed=True,
                start__lte=data["end"],
                end__gte=data["start"],
            )
            return not queryset.exists()

        # if priority reservation and non admin user.
        return False

    def perform_create(self, serializer):
        auto_confirm = False
        data = serializer.validated_data
        auto_confirm = self.should_auto_confirm(data)
        serializer.save(confirmed=auto_confirm)

    def perform_update(self, serializer):
        old_obj = self.get_object()
        new_data = serializer.validated_data
        auto_confirm = old_obj.confirmed
        # if time was changed we need to recalculate auto approval
        if old_obj.start != new_data["start"] or old_obj.end != new_data["end"]:
            if old_obj.confirmed:
                # Recalculate confirmation
                auto_confirm = self.should_auto_confirm(new_data, exists=True)

        serializer.save(confirmed=auto_confirm)


class ItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows bookable items to be viewed.
    """

    queryset = Item.objects.all()
    serializer_class = ItemSerializer
