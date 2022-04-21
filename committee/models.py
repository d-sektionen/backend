from django.db import models
from django.contrib.auth.models import User


class Committee(models.Model):
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=256, default='N/A')
    members = models.ManyToManyField(User, blank=True, related_name='committees')
    treasurer = models.ForeignKey(User, related_name="treasurer_for", null=True, on_delete=models.SET_NULL)
    treasurer_email = models.EmailField(null=True)

    def __str__(self):
        return self.name + " - " + self.description[:32]
