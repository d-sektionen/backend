from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Key(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    order = models.IntegerField(unique=True)
    color = models.CharField(max_length=64)

    def status(self):
        le = LogEntry.objects.filter(
            key=self, returned_successfully=False, taken_successfully=True
        ).order_by("-taken_at")
        return le[0] if le else None

    def __str__(self):
        return self.name


class LogEntry(models.Model):
    key = models.ForeignKey(Key, on_delete=models.CASCADE, related_name="entries")

    taken_at = models.DateTimeField(null=True, blank=True)
    taken_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    taken_successfully = models.BooleanField(default=False)

    returned_at = models.DateTimeField(null=True, blank=True)
    returned_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    returned_successfully = models.BooleanField(default=False)

