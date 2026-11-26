from django import forms
from django.contrib import admin
from django.db import models
from django.urls import reverse

from .models import Photo, PhotoAlbum, PhotoTag


class PhotoImageWidget(forms.ClearableFileInput):
    """Link the current image to the photo download endpoint.

    Photo images are kept in protected storage, so their storage URL
    (/media/...) is not served. They are streamed by the download action
    of PhotoViewSet instead.
    """

    def format_value(self, value):
        value = super().format_value(value)
        if value is None:
            return value

        photo = getattr(value, "instance", None)
        if photo is None or photo.pk is None:
            return value

        url = reverse("photo-download", kwargs={"pk": photo.pk})
        return _DownloadableFile(value, url)


class _DownloadableFile:
    """Wrap a FieldFile so the widget links to a custom URL."""

    def __init__(self, file, url):
        self._file = file
        self.url = url

    def __str__(self):
        return str(self._file)


class PhotoTagAdmin(admin.ModelAdmin):
    pass


class PhotoAlbumAdmin(admin.ModelAdmin):
    pass


class PhotoAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ImageField: {"widget": PhotoImageWidget},
    }


admin.site.register(PhotoTag, PhotoTagAdmin)
admin.site.register(PhotoAlbum, PhotoAlbumAdmin)
admin.site.register(Photo, PhotoAdmin)
