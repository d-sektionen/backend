from django.db import models
from model_utils.managers import InheritanceManager
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status

class Event(models.Model):
  objects = InheritanceManager()

  name = models.CharField(max_length=64)
  archived = models.BooleanField(default=False)

  ACTIONS = []

  def __str__(self):
    return self.name

  # Has to be overwritten when extending
  def on_register(self, user, action):
    return Response({"detail": 'You can not register someone on a plain Event, the Event class should be extended.'}, status.HTTP_400_BAD_REQUEST)

class Doorkeeper(models.Model):
  user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
  event = models.ForeignKey(Event, null=False, on_delete=models.CASCADE)

  class Meta:
    unique_together = ('user', 'event')

# class Restaurant(Event):
#   # ...
#   pass

# class Bar(Event):
#   # ...
#   pass

# nearby_places = Event.objects.filter(location='here').select_subclasses()
# for place in nearby_places:
#   pass