from django.contrib.auth.models import User
from rest_framework import serializers, status
from booking.models import Booking
from rest_framework.response import Response


"""
Checks if the given data from the LogEntry or LogStart corresponds to an actual
instance of a Booking of a car in the database.
"""
def check_invalid_booking(data):
    booking_liu_id = data["booking_liu_id"]

    liu_id_exists = User.objects.filter(username=booking_liu_id).exists()
    if not liu_id_exists:
        return Response(
            {"error": "User with that liu_id does not exist in the database"}, 
            status=status.HTTP_404_NOT_FOUND
        )

    booking_user = User.objects.get(username=booking_liu_id)
    bookings_exist = Booking.objects.filter(user=booking_user).exists()

    if not bookings_exist:
        return Response(
            {"error": "No bookings for that liu_id exist"}, 
            status=status.HTTP_404_NOT_FOUND
        )

    car_booking_exists = False
    bookings = Booking.objects.filter(user=booking_user)

    for booking in bookings:
        if booking.item.name == "Kianu Revs":  # improve this solution?
            car_booking_exists = True

    if not car_booking_exists:
        return Response(
            {"error": "The user with the liu_id you entered does not have a car booking in the database"}, 
            status=status.HTTP_404_NOT_FOUND
        )

    return False
