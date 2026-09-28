from django_ical.views import ICalFeed
from django.utils.timezone import get_current_timezone
from ..booking.models import Booking
from .models import CalendarSubscription


def _booking_username(booking: Booking) -> str:
    name = booking.user.get_full_name()
    if name == "" or name is None:
        name = booking.user.get_username()

    return name


def _items_string(booking: Booking) -> str | None:
    items = ", ".join(map(lambda x: x.name, booking.items.all()))
    if items == "":
        return None

    return items


def _booking_title(booking: Booking, include_username: bool = True) -> str:
    title = f"Bokning av {booking.pool.name}"

    if include_username:
        name = _booking_username(booking)
        title += f" - {name}"

    items = _items_string(booking)
    if items:
        title += f" ({items})"

    return title


def _booking_description(booking: Booking) -> str:
    name = _booking_username(booking)
    items = _items_string(booking)

    description = f"Beskrivning: {booking.description}\n\n"
    description += f"Bokning i pool: {booking.pool.name}\n"
    if items:
        description += f"föremål: {_items_string(booking)}.\n\n"
    description += f"Bokad av: {name}"

    return description


class CalendarFeed(ICalFeed):
    """
    A calendar
    """

    product_id = "-//d-sektionen.se//calendar//SV"
    timezone = str(get_current_timezone())
    file_name = "d-sektionen.ics"
    title = "D-sektionen kalender"

    def get_object(self, request, pk):
        return CalendarSubscription.objects.get(pk=pk)

    def description(self, subscription):
        features = []
        bookable_items = subscription.include_bookable_items.all()

        if subscription.include_bookings_by_user:
            features.append("dina bokningar från bokningssystemet")
        if len(bookable_items) > 0:
            item_names = [i.name for i in bookable_items]

            features.append(f"alla bokningar för: {', '.join(item_names)}")
        features_string = "ingenting" if len(features) == 0 else ", ".join(features)
        return f"Kalender för tjänster på D-sektionens medlemsportal. Prenumerationen innehåller {features_string}."

    def items(self, subscription):
        items = []
        if subscription.include_bookings_by_user:
            bookings = []

            for booking in Booking.objects.filter(user=subscription.user):
                title = _booking_title(booking, include_username=False)
                description = _booking_description(booking)
                bookings.append(
                    {
                        "id": f"booking-user-{booking.id}",
                        "start": booking.start,
                        "end": booking.end,
                        "description": description,
                        "title": title,
                    }
                )

            items.extend(bookings)

        for pool in subscription.include_bookable_items.all():
            bookings = []

            for booking in Booking.objects.filter(pool=pool):
                title = _booking_title(booking)
                description = _booking_description(booking)

                bookings.append(
                    {
                        "id": f"booking-all-{booking.id}",
                        "start": booking.start,
                        "end": booking.end,
                        "description": description,
                        "title": title,
                    }
                )

            items.extend(bookings)

        return items

    def item_title(self, item):
        return item["title"]

    def item_guid(self, item):
        return item["id"] + "@d-sektionen.se"

    def item_description(self, item):
        return item["description"]

    def item_start_datetime(self, item):
        return item["start"]

    def item_end_datetime(self, item):
        return item["end"]

    def item_link(self, item):
        return ""

    def item_location(self, item):
        # Workaround to show descriptions in Google calendar
        return item["description"]
