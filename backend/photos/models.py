from django.db import models
from .utils import get_photo_path
from .storage import protected_storage

class PhotoTag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class PhotoAlbum(models.Model):
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title

class Photo(models.Model):
    title = models.CharField(max_length=100)
    featured = models.BooleanField(default=False)
    date = models.DateTimeField()
    tags = models.ManyToManyField(PhotoTag, blank=True, related_name="photos")
    album = models.ForeignKey(PhotoAlbum, null=True, on_delete=models.SET_NULL, related_name="photos")
    image = models.ImageField(blank=False, upload_to=get_photo_path, storage=protected_storage)

    def __str__(self):
        return self.title
