from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import F
from rest_framework import viewsets, views, status
from rest_framework.decorators import list_route
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from storage.models import StorageRoom, Location, Booking, Object
from storage.serializers import StorageRoomSerializer, LocationSerializer, BookingSerializer, ObjectSerializer

class StorageRoomViewSet(viewsets.ModelViewSet):
    queryset = StorageRoom.objects.all()
    serializer_class = StorageRoomSerializer
    
class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

class ObjectViewSet(viewsets.ModelViewSet):
    queryset = Object.objects.all()
    serializer_class = ObjectSerializer
