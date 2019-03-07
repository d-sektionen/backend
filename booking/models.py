from django.db import models
from django.contrib.auth.models import User
from .validators import validate_datetime_future, validate_datetime_within_year
from django.core.exceptions import ValidationError
from datetime import timedelta

class Item(models.Model):
  name = models.CharField(max_length=32, unique=True)
  description = models.TextField(max_length=128)

  def __str__(self):
    return self.name
  

class Booking(models.Model):
  start = models.DateTimeField(validators=[validate_datetime_future])
  end = models.DateTimeField(validators=[validate_datetime_within_year])
  user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
  item = models.ForeignKey(Item, null=False, on_delete=models.CASCADE)
  description = models.TextField()

  def __str__(self):
    return self.user.username + ' - ' + self.description[:32]

  def clean(self):
    # Start should be before end
    if self.start > self.end:
      raise ValidationError('Booking should start before it ends.')
    # Check lowest duration
    if self.start + timedelta(minutes=30) > self.end:
      raise ValidationError('Booking should be at least 30 minutes.')
    # Check longest duration
    if self.start + timedelta(days=7) < self.end:
      raise ValidationError('Booking should be at most 7 days.')


    # Check overlap
    if Booking.objects\
      .filter(item=self.item)\
      .exclude(id=self.id)\
      .filter(start__lte=self.end, end__gte=self.start)\
      .exists():
      raise ValidationError('Booking overlaps with another booking.')


  