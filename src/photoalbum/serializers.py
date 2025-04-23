from .models import Photo, Committee
from rest_framework import serializers


class PhotoSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    committee = serializers.SlugRelatedField(
        slug_field="name", queryset=Committee.objects.all()
    )

    class Meta:
        model = Photo
        fields = "__all__"
        read_only_fields = ("id",)
