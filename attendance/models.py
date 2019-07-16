from django.db import models
from checkin.models import Event
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status

from membership.utils import check_membership

class Occurrence(Event):
  ACTIONS = ['Registrera', 'Jonglera', 'Marchera']

  members_only = models.BooleanField(default=False)
  clear_data = models.DateField()
  attendant_limit = models.IntegerField(default=0)
  attendants = models.ManyToManyField(User, related_name='+', blank=True)

  def on_register(self, user, action):
    already_registered = self.attendants.filter(pk=user.pk).exists()
    # TODO: actions

    if already_registered:
      return Response({"detail": user.username + ' is already registered.'}, status.HTTP_400_BAD_REQUEST)

    count = self.attendants.all().count()
    if count >= self.attendant_limit and self.attendant_limit != 0:
      return Response({"detail": 'Limit of ' + str(self.attendant_limit) + ' users has been reached.'}, status.HTTP_400_BAD_REQUEST)

    if self.members_only and not check_membership(user.username):
      return Response({"detail": 'User is not a member of D-sektionen.'}, status.HTTP_400_BAD_REQUEST)

    self.attendants.add(user)
    return Response({"detail": user.username + ' was successfully registered.', 'icon': 'FiUserCheck'}, status.HTTP_200_OK)


