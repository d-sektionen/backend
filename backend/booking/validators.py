from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from .models import Booking


def validate_datetime_future(datetime):
    if datetime < timezone.now():
        raise ValidationError("Date is in the past.")


def validate_datetime_within_year(datetime):
    if datetime > timezone.now() + timedelta(days=365):
        raise ValidationError("Date is further than a year into the future.")


def should_auto_confirm(data, instance):
    # If item pool requires confirmation, do not auto confirm.
    if data["pool"].requires_confirmation:
        return False

    # If booking is a normal booking.
    if not data["restricted_timeslot"]:
        queryset = Booking.objects.all()  # type: ignore[attr-defined]

        # on update don't compare with self.
        if instance:
            queryset = queryset.exclude(pk=instance.id)

        # If no confirmed restricted timeslot is overlapping with booking, auto confirm.
        queryset = Booking.objects.filter(  # type: ignore[attr-defined]
            pool=data["pool"],
            restricted_timeslot=True,
            confirmed=True,
            start__lte=data["end"],
            end__gte=data["start"],
        )
        return not queryset.exists()
