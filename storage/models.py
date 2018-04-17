from datetime import date
from django.db import models
from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError

from account.models import is_user_in_group


class StorageRoom(models.Model):
    name = models.TextField()
    longitude = models.TextField()
    latitude = models.TextField()
    description = models.TextField(blank=True)
    model_url = models.TextField(blank=True)

class Location(models.Model):
    name = models.TextField()
    room = models.ForeignKey(StorageRoom, null=False, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    can_contain_objects = models.BooleanField()

    def current_booking(self):
        today = date.today()
        try:
            return Booking.objects.get(location=self, start_date__lte=today, end_date__gte=today)
        except Booking.DoesNotExist:
            return None

    def has_permissions(self, user):
        current_booking = self.current_booking()
        if current_booking is not None:
            return current_booking.has_permissions(user)
        else:
            return False

class Booking(models.Model):
    group = models.ForeignKey(Group, null=False, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, null=False, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    until_further_notice = models.BooleanField()
    description = models.TextField()

    def clean(self):
        if self.end_date is not None and self.until_further_notice:
            raise ValidationError('end_date and until_further_notice must be mutually exclusive')
        if self.end_date is None and not self.until_further_notice:
            raise ValidationError('Must have end_date or until_further_notice')
        if self.end_date is not None and self.end_date < self.start_date:
            raise ValidationError('start_date later than end_date')

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Booking, self).save(*args, **kwargs)

    def has_permissions(self, user):
        return is_user_in_group(self.group, user)

class Object(models.Model):
    name = models.TextField()
    location = models.ForeignKey(Location, null=False, on_delete=models.CASCADE)
    description = models.TextField()
    in_date = models.DateField(default=date.today)
    amount = models.IntegerField()
    belongs_to = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE)
    private = models.BooleanField(default=False)
    can_be_borrowed = models.BooleanField(default=False)
    

    def has_permissions(self, user):
        return self.location.has_permissions(user)
