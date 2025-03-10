from django.db import models
from committee.models import Committee


class Photo(models.Model):
    title = models.CharField(max_length=100)
    date = models.DateTimeField()
    event = models.CharField(max_length=100)
    tags = models.JSONField(default=list, blank=True)
    image = models.ImageField(
        blank=False
    )  # TODO: Might not be this format, just a placeholder atm
    committee = models.ForeignKey(Committee, on_delete=models.SET_NULL, null=True)

    # TODO: Check how this handles itself overall, might be a bit of rework needed for committee/year handling

    def __str__(self):
        return self.title
