from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta


def validate_datetime_future(datetime):
    if datetime < timezone.now():
        raise ValidationError("Date is in the past.")


def validate_datetime_within_year(datetime):
    if datetime > timezone.now() + timedelta(days=365):
        raise ValidationError("Date is further than a year into the future.")
