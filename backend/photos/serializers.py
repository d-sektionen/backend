from django.conf import settings
from django.contrib.auth.models import User

from backend.account.serializers import SimpleUserSerializer

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
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=PhotoTag.objects.all(),
        source="tags",
        required=False,
    )
    album = PhotoAlbumSerializer(read_only=True)
    album_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=PhotoAlbum.objects.all(),
        source="album",
        required=False,
        allow_null=True,
    )
    image = serializers.ImageField(write_only=True)
    image_url = serializers.SerializerMethodField()
    user = SimpleUserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=User.objects.all(),
        source="user",
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Photo
        fields = (
            "id",
            "title",
            "featured",
            "date",
            "tags",
            "tag_ids",
            "album",
            "album_id",
            "image",
            "image_url",
            "user",
            "user_id",
        )
        read_only_fields = ("id", "image_url",)

    def get_image_url(self, obj):
        return f"{settings.BASE_URL}/photos/photos/{obj.id}/download"


