from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import F
from rest_framework import viewsets, views, status
from rest_framework.decorators import list_route
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from django import forms
from django.contrib.auth.models import Group

from django.db import transaction
from django.db.models import F
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

#TODO : Fixa så att mutex:en inte fuckar
    def create(self, request):
        location = request.data['location']
        start_date = request.data['start_date']
        end_date = request.data['end_date']
        if "until_further_notice" in request.data:
            until_further_notice = request.data['until_further_notice']
        else:
            until_further_notice = False
        
        if until_further_notice:
            if Booking.objects.filter(until_further_notice=True, location=location).exists(): 
                return Response({'error': 'Finns redan en until_further_notice-bokning'}, status=status.HTTP_403_FORBIDDEN)          

            if Booking.objects.filter(end_date__gte=start_date, location=location).exists():
                return Response({'error': 'Until_further_notice men någon annan pågår'}, status=status.HTTP_403_FORBIDDEN)
        else:
            if Booking.objects.filter(start_date=start_date, end_date=end_date, location=location).exists():
                return Response({'error': 'Dubbelbokning'}, status=status.HTTP_403_FORBIDDEN)

            if Booking.objects.filter(start_date__lte=start_date, end_date__gte=start_date, location=location).exists():
                return Response({'error': 'Start under pågående bokning'}, status=status.HTTP_403_FORBIDDEN)

            if Booking.objects.filter(start_date__gte=start_date, start_date__lte=end_date, location=location).exists():
                return Response({'error': 'Slut under pågående bokning'}, status=status.HTTP_403_FORBIDDEN)

        return super(BookingViewSet, self).create(request)

class ObjectViewSet(viewsets.ModelViewSet):
    queryset = Object.objects.all()
    serializer_class = ObjectSerializer