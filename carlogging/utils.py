from django.contrib.auth.models import User
from rest_framework import serializers, status
from booking.models import Booking
from rest_framework.response import Response


def get_booking(liu_id, check_for_trailer=False) -> Booking:
    """
    Returns a booking that corresponds to a given LiU-ID if it exists.
    """
    user = User.objects.get(username=liu_id)

    bookings = Booking.objects.filter(user=user, item__category__name='Bilrelaterat')
    if check_for_trailer:
        bookings = bookings.filter(item__name='Släp', carlogging_entries_trailer_booking=None)
    else:
        bookings = bookings.filter(carlogging_starts_car_booking=None).exclude(item__name='Släp')

    return bookings.order_by('start').first()


def validate_booking_user(liu_id, check_for_trailer=False):
    """
    Validate that there's a user that corresponds to a given LiU-ID.\n
    Returns an error response if invalid, otherwise False.
    """
    if not User.objects.filter(username=liu_id).exists():
        return Response(
            {'error': f'User with the LiU-ID "{liu_id}" does not exist.',
             'status_text': f'Det finns ingen användare med LiU-ID:t "{liu_id}".'}, 
            status=status.HTTP_404_NOT_FOUND
        )
        
    booking = get_booking(liu_id, check_for_trailer)
    if booking is None:
        if check_for_trailer:
            return Response(
                {'error': f'No trailer booking corresponds with the LiU-ID "{liu_id}"!',
                 'status_text': f'Ingen släpbokning korresponderar med LiU-ID:t "{liu_id}"!'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(
            {'error': f'No car booking corresponds with the LiU-ID "{liu_id}"!',
             'status_text': f'Ingen bilbokning korresponderar med LiU-ID:t "{liu_id}"!'}, 
            status=status.HTTP_404_NOT_FOUND
        )

    return False


def _validate_data(data, essential_key_types):
    """
    Validate the data of a generic POST request.\n
    Returns an error response if invalid, otherwise False.
    """
    # Check for missing keys
    missing_keys = list()
    for key in essential_key_types:
        if key not in data:
            missing_keys.append(key)
    if missing_keys:
        missing_keys_str = str(missing_keys)[1:-1]  # Removes the square brackets
        return Response(
            {'error': f'The data {missing_keys_str} is missing!',
             'status_text': f'Datan {missing_keys_str} fattas!'},
            status.HTTP_400_BAD_REQUEST
        )

    # Check for invalid key types
    for key, value in essential_key_types.items():
        cmp_value = type(data[key])
        if cmp_value != value:
            return Response(
                {'error': f'The data "{key}" should be of type "{value}", not "{cmp_value}"!',
                'status_text': f'Datan "{key}" borde vara av typen "{value}", inte "{cmp_value}"!'},
                status.HTTP_400_BAD_REQUEST
            )
    
    return False


def validate_start_data(data):
    """
    Validate the data of a LogStart POST request.\n
    Returns an error response if invalid, otherwise False.
    """
    essential_key_types = {
        'booking_liu_id': str,
        'kilometers': int,
        'message': str,
        'car_cleaned': bool
    }
    return _validate_data(data, essential_key_types)


def validate_entry_data(data):
    """
    Validate the data of a LogEntry POST request.\n
    Returns an error response if invalid, otherwise False.
    """
    essential_key_types = {
        'booking_liu_id': str,
        'kilometers': int,
        'message': str,
        'car_cleaned': bool,
        'trailer': bool
    }
    return _validate_data(data, essential_key_types)
