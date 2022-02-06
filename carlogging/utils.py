from django.contrib.auth.models import User
from rest_framework.response import Response

from booking.models import Booking


def get_unlogged_booking(user: User, trailer: bool) -> Booking:
    """Returns the oldest unlogged car or trailer booking for the specified user."""
    bookings = Booking.objects.filter(user=user, item__category__name='Bilrelaterat')
    if trailer:
        bookings = bookings.filter(item__name='Släp', carlogging_entries_trailer_booking=None)
    else:
        bookings = bookings.filter(carlogging_starts_car_booking=None).exclude(item__name='Släp')
    return bookings.order_by('start').first()


def validate_request_data(data: dict, data_types: dict) -> Response:
    """
    Validates that the essential data of a request exists and is of the right data types.\n
    Returns a 400 BAD REQUEST response if invalid, otherwise None.
    """
    data_resp = dict()
    for data_key, data_type in data_types.items():
        if data_key not in data.keys():
            data_resp[data_key] = 'Detta måste fyllas i'
        elif type(data[data_key]) != data_type:
            data_resp[data_key] = f'Detta måste vara av typen {data_type}'

    if data_resp:
        data_resp['status_text'] = 'Det var något fel på den inskickade datan'
        return data_resp
    return None