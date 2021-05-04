from django.contrib.auth.models import User
from rest_framework import serializers
from booking.models import Booking


"""
Checks if the given data from the LogEntry or LogStart corresponds to an actual
instance of a Booking of a car in the database.
"""
def check_valid_booking(validated_data):
    booking_liu_id = validated_data["booking_liu_id"]

    liu_id_exists = User.objects.filter(username=booking_liu_id).exists()
    if not liu_id_exists:
        raise serializers.ValidationError(
            "User with that liu_id does not exist in the database"
        )

    booking_user = User.objects.get(username=booking_liu_id)
    bookings_exist = Booking.objects.filter(user=booking_user).exists()

    if not bookings_exist:
        raise serializers.ValidationError(
            "No bookings for that liu_id exist"
        )

    car_booking_exists = False
    bookings = Booking.objects.filter(user=booking_user)

    for booking in bookings:
        if booking.item.name == "Kianu Revs":  # ändra lösning???
            car_booking_exists = True

    if not car_booking_exists:
        raise serializers.ValidationError(
            "The user with the liu_id you entered does not have a car booking in the database"
        )
