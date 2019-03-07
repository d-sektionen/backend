from .models import Booking, Item
from rest_framework import viewsets
from django.utils import timezone
from .serializers import BookingSerializer, ItemSerializer
from .permissions import BookingPermissions

class BookingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows bookings to be viewed, created, edited or deleted.
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = (BookingPermissions, )

    def get_queryset(self):
        queryset = self.queryset
        item = self.request.query_params.get('item', None)
        future = self.request.query_params.get('future', None)
        user = self.request.query_params.get('user', None)
        if user == "me": user = self.request.user.id

        if item:
          queryset = queryset.filter(item=item)
        if future != None:
          queryset = queryset.filter(end__gt=timezone.now())
        if user:
          queryset = queryset.filter(user=user)
        return queryset


class ItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows bookable items to be viewed.
    """
    queryset = Item.objects.all()
    serializer_class = ItemSerializer