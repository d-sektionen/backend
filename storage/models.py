from django.db import models
from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError

class StorageRoom(models.Model):
    name = models.TextField()
    longitude = models.TextField()
    latitude = models.TextField()

class Location(models.Model):
    name = models.TextField()
    room = models.ForeignKey(StorageRoom, null=False, on_delete=models.CASCADE)
    can_contain_objects = models.BooleanField()

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

class Object(models.Model):
    name = models.TextField()
    location = models.ForeignKey(Location, null=False, on_delete=models.CASCADE)
    description = models.TextField()
    in_date = models.DateField()
    out_date = models.DateField()
    amount = models.IntegerField()
    belongs_to = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE)


