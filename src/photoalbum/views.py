from rest_framework import viewsets
from django.utils.dateparse import parse_datetime

from photoalbum.models import Photo
from photoalbum.permissions import PhotoPermissions
from photoalbum.serializers import PhotoSerializer


class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all()

    serializer_class = PhotoSerializer
    permission_classes = (PhotoPermissions,)
    # TODO: Pagination class if we want some custom pagination, something like pagination_class = CustomPagination

    def get_queryset(self):
        queryset = super().get_queryset()

        # Parse and apply datetime filtering
        time_start = self.request.query_params.get("time_start", None)
        time_end = self.request.query_params.get("time_end", None)

        if time_start is not None:
            parsed_time_start = parse_datetime(time_start)
            if parsed_time_start:
                queryset = queryset.filter(date__gte=time_start)
        if time_end is not None:
            parsed_time_end = parse_datetime(time_end)
            if parsed_time_end:
                queryset = queryset.filter(date__lte=time_end)

        # Check for other filter input
        event = self.request.query_params.get("event", None)
        tags = self.request.query_params.get("tags", None)
        committee = self.request.query_params.get("committee", None)

        if event:
            queryset = queryset.filter(event__enabled=True, event__id=event)

        # Tags require some special treatment since it is handled as a JSONField
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
            if tag_list:
                queryset = queryset.filter(tags__contains=tag_list)

        if committee:
            queryset = queryset.filter(committee__name=committee)

        return queryset
