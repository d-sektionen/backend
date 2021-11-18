from django.contrib.auth.models import User
from rest_framework import serializers, status
from booking.models import Booking
from rest_framework.response import Response


def check_invalid_booking(data):
    """
    Checks if the given data from the LogEntry or LogStart corresponds to an actual
    instance of a Booking of a car in the database.
    """
    booking_liu_id = data["booking_liu_id"]

    liu_id_exists = User.objects.filter(username=booking_liu_id).exists()
    if not liu_id_exists:
        return Response(
            {"error": "User with that liu_id does not exist in the database",
            "status_text": "Det finnns ingen användare med det LiU-ID:t."}, 
            status=status.HTTP_404_NOT_FOUND
        )

    booking_user = User.objects.get(username=booking_liu_id)
    bookings_exist = Booking.objects.filter(user=booking_user).exists()

    if not bookings_exist:
        return Response(
            {"error": "No bookings for that liu_id exist",
            "status_text": "Det finns inga bokningar för en användare med det LiU-ID:t."}, 
            status=status.HTTP_404_NOT_FOUND
        )

    car_booking_exists = False
    bookings = Booking.objects.filter(user=booking_user)

    for booking in bookings:
        if booking.item.name == "Kianu Revs":  # improve this solution?
            car_booking_exists = True

    if not car_booking_exists:
        return Response(
            {"error": "The user with the liu_id you entered does not have a car booking in the database",
            "status_text": "Det finns inget LiU-ID:t med en bokning av bilen."}, 
            status=status.HTTP_404_NOT_FOUND
        )

    return False


def check_invalid_start_data(data):
    '''Checks if the data of a LogStart is of the correct data type and if it exists.'''

    essential_keys = [
        'booking_liu_id',
        'start_km',
        'start_message',
        'start_car_cleaned'
    ]

    missing_keys = []
    for key in essential_keys:
        if key not in data:
            missing_keys.append(key)
    if missing_keys:
        return Response(
            {'error': f'Data that is necessary to complete the request is missing: {missing_keys}',
            'status_text': f'Det fattas data som krävs: {missing_keys}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    data_types = {
        'booking_liu_id': str,
        'start_km': int,
        'start_message': str,
        'start_car_cleaned': bool
    }

    for key, data_type in data_types.items():
        if type(data[key]) != data_type:
            return Response(
                {'error': f'The request data "{key}" should be of type "{data_type}"!',
                 'status_text': f'Datan "{key}" borde vara av typen "{data_type}"'},
                status=status.HTTP_400_BAD_REQUEST
            )

    return False


def check_invalid_entry_data(data):
    '''Checks if the request data of a LogEntry is of the correct data type and if it exists.'''

    essential_keys = [
        'booking_liu_id',
        'end_km',
        'end_message',
        'end_car_cleaned',
        'car_days',
        'trailer_days',
        'trailer',
        'active_member'
    ]

    missing_keys = []
    for key in essential_keys:
        if key not in data:
            missing_keys.append(key)
    if missing_keys:
        return Response(
            {'error': f'Data that is necessary to complete the request is missing: {missing_keys}',
            'status_text': f'Det fattas data som krävs: {missing_keys}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    data_types = {
        'booking_liu_id': str,
        'end_km': int,
        'end_message': str,
        'end_car_cleaned': bool,
        'car_days': int,
        'trailer_days': int,
        'trailer': bool,
        'active_member': bool
    }

    for key, data_type in data_types.items():
        if type(data[key]) != data_type:
            return Response(
                {'error': f'The request data "{key}" should be of type "{data_type}"!',
                 'status_text': f'Datan "{key}" borde vara av typen "{data_type}"'},
                status=status.HTTP_400_BAD_REQUEST
            )

    return False
