from django_ical.views import ICalFeed
from django.utils.timezone import get_current_timezone
from booking.models import Booking

from .models import CalendarSubscription


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
        if subscription.include_bookings_by_user:
            features.append("dina bokningar från bokningssystemet")
        features_string = "ingenting" if len(features) == 0 else ", ".join(features)
        return f"Kalender för tjänster på D-sektionens medlemsportal. Prenumerationen innehåller {features_string}."

    def items(self, subscription):
        items = []
        if subscription.include_bookings_by_user:
            bookings = [
                {
                    "id": f"booking-{b.id}",
                    "start": b.start,
                    "end": b.end,
                    # TODO extend with link etc
                    "description": b.description,
                    "title": f"Bokning av {b.item.name}",
                }
                for b in Booking.objects.filter(user=subscription.user)
            ]
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
