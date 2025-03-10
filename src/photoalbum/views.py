from rest_framework import viewsets

from photoalbum.models import Photo
from photoalbum.permissions import PhotoPermissions
from photoalbum.serializers import PhotoSerializer


class PhotoViewSet(viewsets.ModelViewSet):
    # TODO: This filtering needs refactoring, can't use True value for datetime object etc.
    queryset = Photo.objects.filter(
        date__gte=True,
        date__lte=True,
        event__enabled=True,
        tags__enabled=True,
        committee__name=True,
    )
    serializer_class = PhotoSerializer
    permission_classes = (PhotoPermissions,)
    # TODO: Pagination class if we want some custom pagination, something like pagination_class = CustomPagination

    def get_queryset(self):
        # TODO: same as above, needs fixing to actual things not just True
        queryset = Photo.objects.filter(
            date__gte=True,
            date__lte=True,
            event__enabled=True,
            tags__enabled=True,
            committee__name=True,
        )
        time_start = self.request.query_params.get("time_start", None)
        time_end = self.request.query_params.get(
            "time_end", None
        )  # TODO: Check this date handling, maybe a default val?
        event = self.request.query_params.get("event", None)
        tags = self.request.query_params.get("tags", None)
        committee = self.request.query_params.get("committee", None)

        if time_start is not None:
            queryset = queryset.filter(time_start=time_start)
        if time_end is not None:
            queryset = queryset.filter(time_end=time_end)
        if event:
            queryset = queryset.filter(event=event)
        if tags:
            queryset = queryset.filter(tags=tags)
        if committee:
            queryset = queryset.filter(committee=committee)
        return queryset
