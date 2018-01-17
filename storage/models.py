from django.db import models
from django.contrib.auth.models import Group, User

class StorageRoom(models.Model):
    name = models.TextField()
    longitude = models.TextField()
    latitude = models.TextField()

class Location(models.Model):
    name = models.TextField()
    room = models.ForeignKey(Room, null=False)
    can_contain_objects = models.BooleanField()

class Booking(models.Model):
    group = models.ForeignKey(Group, null=False)
    location = models.ForeignKey(Location, null=False)
    start_date = models.DateField()
    until_further_notice = models.BooleanField()
    description = models.TextField()

class Object(models.Model):
    name = models.TextField()
    location = models.ForeignKey(Place, null=False)
    description = models.TextField()
    in_date = models.DateField()
    out_date = models.DateField()
    amount = models.IntegerField()
    belongs_to = ForeignKey(Object)