from rest_framework import viewsets
from rest_framework.decorators import action
from django.utils.dateparse import parse_datetime
from django.http import FileResponse
from django.conf import settings
from django.http import HttpResponse

from .models import Photo, PhotoAlbum, PhotoTag
from .permissions import PhotoPermissions
from .serializers import PhotoAlbumSerializer, PhotoSerializer, PhotoTagSerializer

class PhotoTagViewSet(viewsets.ModelViewSet):
    queryset = PhotoTag.objects.all()
    serializer_class = PhotoTagSerializer

class PhotoAlbumViewSet(viewsets.ModelViewSet):
    queryset = PhotoAlbum.objects.all()

    serializer_class = PhotoAlbumSerializer

class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all()

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
                queryset = queryset.filter(tags__contains=tag_list)

        if album:
            queryset = queryset.filter(album__id=album)

        return queryset

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        obj = self.get_object()

        filename = obj.image.name.split('/')[-1]
        ext = filename.split('.')[-1]

        content_type = f'image/{ext}'
        
        # read the full image and pass it through (this is slow)
        return FileResponse(obj.image.open('rb'), content_type=content_type)
