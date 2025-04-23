from django.db import models
from committee.models import Committee


def get_photo_path(instance, filename):
    ext = filename.split(".")[-1]
    return f"photoalbum/{instance.date.year}/{instance.title}.{ext}"


class Photo(models.Model):
    title = models.CharField(max_length=100)
    date = models.DateTimeField()
    event = models.CharField(max_length=100)
    tags = models.JSONField(default=list, blank=True)
    image = models.ImageField(blank=False, upload_to=get_photo_path)
    committee = models.ForeignKey(
        Committee, on_delete=models.SET_NULL, null=True, to_field="name"
    )

    def __str__(self):
        return self.title
