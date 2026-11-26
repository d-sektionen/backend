import mimetypes
import rest_framework
from rest_framework import viewsets
from rest_framework.decorators import action
from django.utils.dateparse import parse_datetime
from django.http import FileResponse

from .models import Photo, PhotoAlbum, PhotoTag
from .permissions import PhotoMetaPermissions, PhotoPermissions
from .serializers import PhotoAlbumSerializer, PhotoSerializer, PhotoTagSerializer


class PhotoTagViewSet(viewsets.ModelViewSet):
    queryset = PhotoTag.objects.all()

    serializer_class = PhotoTagSerializer
    permission_classes = (PhotoMetaPermissions,)


class PhotoAlbumViewSet(viewsets.ModelViewSet):
    queryset = PhotoAlbum.objects.all()

    serializer_class = PhotoAlbumSerializer
    permission_classes = (PhotoMetaPermissions,)


class PhotoViewSet(viewsets.ModelViewSet):
    queryset = (
        Photo.objects.all().select_related("album", "user").prefetch_related("tags")
    )

    serializer_class = PhotoSerializer
    permission_classes = (PhotoPermissions,)
    # TODO: Pagination class if we want some custom pagination, something like pagination_class = CustomPagination

    def get_queryset(self):
        queryset = super().get_queryset()

        date_start = self.request.query_params.get("date_start", None)
        date_end = self.request.query_params.get("date_end", None)
        tags = self.request.query_params.get("tags", None)
        album = self.request.query_params.get("album", None)

        if date_start is not None:
            parsed_time_start = parse_datetime(date_start)
            if parsed_time_start:
                queryset = queryset.filter(date__gte=date_start)

        if date_end is not None:
            parsed_time_end = parse_datetime(date_end)
            if parsed_time_end:
                queryset = queryset.filter(date__lte=date_end)

        if tags:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
            if tag_list:
                # .distinct() is used to avoid duplicates when a photo matches multiple tags
                queryset = queryset.filter(tags__name__in=tag_list).distinct()

        if album:
            try:
                album = int(album)
            except ValueError:
                raise rest_framework.exceptions.ValidationError(
                    "Album ID must be an integer."
                )

            queryset = queryset.filter(album__id=album)

        return queryset

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        obj = self.get_object()

        filename = obj.image.name.split("/")[-1]
        content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"

        # read the full image and pass it through
        return FileResponse(
            obj.image.open("rb"), content_type=content_type, as_attachment=True
        )
