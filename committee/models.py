from django.db import models
from django.contrib.auth.models import User


class Committee(models.Model):
    name = models.CharField(max_length=128)
    members = models.ManyToManyField(User, blank=True, related_name='committees')
    contact = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)