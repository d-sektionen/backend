from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from post_office import mail

from backend.booking.validators import should_auto_confirm

from ..app.permissions import FixedDjangoModelPermissions
from ..app.utils import render_email
from .models import Booking, ItemPool
from .serializers import BookingSerializer, ItemSerializer
from .serializers import BookingSerializer, DenyBookingSerializer, ItemSerializer
from .permissions import BookingPermissions
from .view_helpers import notify_webhook_unconfirmed_booking


class BookingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows bookings to be viewed, created, edited or deleted.
    """

    queryset = Booking.objects.filter(pool__enabled=True)  # type: ignore[attr-defined]
    serializer_class = BookingSerializer
    permission_classes = (BookingPermissions,)

    def get_queryset(self):
        queryset = Booking.objects.filter(pool__enabled=True)  # type: ignore[attr-defined]
        pool = self.request.query_params.get("pool", None)
        future = self.request.query_params.get("future", None)
        user = self.request.query_params.get("user", None)
        confirmed = self.request.query_params.get("confirmed", None)
        restricted_timeslot = self.request.query_params.get("restricted_timeslot", None)
        after = self.request.query_params.get("after", None)
        before = self.request.query_params.get("before", None)

        if user == "me":
            user = self.request.user.id

        if pool:
            queryset = queryset.filter(pool=pool)
        if future is not None:
            queryset = queryset.filter(end__gt=timezone.now())
        if after is not None:
            queryset = queryset.filter(start__gt=after)
        if before is not None:
            queryset = queryset.filter(end__lt=before)
        if user:
            queryset = queryset.filter(user=user)
        if confirmed:
            queryset = queryset.filter(confirmed=confirmed)
        if restricted_timeslot:
            queryset = queryset.filter(restricted_timeslot=restricted_timeslot)
        return queryset

    @action(
        detail=True,
        methods=["put"],
        permission_classes=[FixedDjangoModelPermissions],
    )
    def confirm(self, request, pk=None):
        booking = self.get_object()
        booking.confirmed = True
        booking.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        auto_confirm = False
        data = serializer.validated_data
        auto_confirm = should_auto_confirm(data, instance=None)
        serializer.save(confirmed=auto_confirm)

        if auto_confirm is False:
            notify_webhook_unconfirmed_booking(data, False)

    def perform_update(self, serializer):
        old_obj = self.get_object()
        new_data = serializer.validated_data
        auto_confirm = old_obj.confirmed
        # if time was changed we need to recalculate auto approval
        if old_obj.start != new_data["start"] or old_obj.end != new_data["end"]:
            if old_obj.confirmed:
                # Recalculate confirmation
                auto_confirm = should_auto_confirm(new_data, self.get_object())

        serializer.save(confirmed=auto_confirm)

        if auto_confirm is False:
            notify_webhook_unconfirmed_booking(new_data, True)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[FixedDjangoModelPermissions],
    )
    def deny(self, request, pk=None):
        serializer = DenyBookingSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        booking = self.get_object()
        booking.delete()

        # Notify the user that the booking has been denied.
        subject, content = render_email(
            "email/denied_booking",
            context={
                "item": booking.item.name,
                "startdate": booking.start,
                "reason": serializer.validated_data["reason"],
            },
        )
        mail.send(
            recipients=[booking.user.email], subject=subject, html_message=content
        )

        return Response(status=status.HTTP_204_NO_CONTENT)


class ItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows bookable items to be viewed.
    """

    queryset = ItemPool.objects.filter(enabled=True)  # type: ignore[attr-defined]
    serializer_class = ItemSerializer
