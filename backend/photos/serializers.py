from django.conf import settings

from .models import Photo, PhotoAlbum, PhotoTag
from rest_framework import serializers


class PhotoTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoTag
        fields = (
            "id",
            "name",
        )
        read_only_fields = ("id",)

class PhotoAlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoAlbum
        fields = (
            "id",
            "title",
            "description",
        )
        read_only_fields = ("id",)


class PhotoSerializer(serializers.ModelSerializer):
    tags = PhotoTagSerializer(many=True, read_only=True)
    album = PhotoAlbumSerializer(read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = (
            "id",
            "title",
            "featured",
            "date",
            "tags",
            "album",
            "image_url"
        )
        read_only_fields = ("id", "image_url",)

    def get_image_url(self, obj):
        return f"{settings.BASE_URL}/photos/photos/{obj.id}/download"


