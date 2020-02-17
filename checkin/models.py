from django.db import models
from model_utils.managers import InheritanceManager
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status

class EventBase(models.Model):
  objects = InheritanceManager()

  name = models.CharField(max_length=64)
  archived = models.BooleanField(default=False)
  clear_data = models.DateField()
  ACTIONS = []

  def __str__(self):
    return self.name

  # Has to be overwritten when extending
  def on_register(self, user, action):
    return Response({"detail": 'You can not register someone on an EventBase, the EventBase class should be extended.'}, status.HTTP_400_BAD_REQUEST)

  # TODO: Define get_event_status
  def get_status_message(self):
    return ""

class Doorkeeper(models.Model):
  user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
  event = models.ForeignKey(EventBase, null=False, on_delete=models.CASCADE)

  class Meta:
    unique_together = ('user', 'event')