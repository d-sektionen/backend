from django.db import models
from django.contrib.auth.models import User


class Committee(models.Model):
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=256, default='N/A')
    members = models.ManyToManyField(User, blank=True, related_name='committees')
    contact = models.ForeignKey(User, related_name='contact_for', null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name + " - " + self.description[:32]
