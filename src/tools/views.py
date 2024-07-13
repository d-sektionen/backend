from django.http.response import JsonResponse
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import viewsets
from icalendar import Calendar, Event
import datetime
from django.utils import timezone
from django.conf import settings

CAL_URL = settings.CAL_URL
LOCAL_TIMEZONE = datetime.timedelta(hours=2)


def normalize_date(date):
    return timezone.make_aware(datetime.datetime(date.year, date.month, date.day))


class SectionCalendarViewSet(viewsets.ViewSet):
    """
    WIP
    Parses the D-sektionen calendar and creates a Django REST Framework endpoint for it.

    Inspiration from https://github.com/bsab/icstojson/blob/master/app.py
    """

    permission_classes = (AllowAny,)

    def list(self, request):
        r = request.get(CAL_URL)  # TODO: Cache request for a few minutes.
        if r.status_code == 200:
            cal = Calendar.from_ical(r.text)
            data = {}
            conversions = {
                "X-WR-CALDESC": "description",
                "X-WR-CALNAME": "name",
                "X-WR-TIMEZONE": "timezone",
                "CALSCALE": "calscale",
                "METHOD": "method",
                "PRODID": "prodid",
                "VERSION": "version",
            }
            for item in cal.items():
                if item[0] in conversions:
                    data[conversions[item[0]]] = item[1]
            data["url"] = CAL_URL
            data["events"] = []

            not_started = request.query_params.get("not_started") is not None
            not_ended = request.query_params.get("not_ended") is not None

            for event in cal.walk("VEVENT"):
                if isinstance(event, Event):
                    now = timezone.now()
                    start = (
                        event.decoded("DTSTART") if "DTSTART" in event else ""
                    ) + LOCAL_TIMEZONE
                    end = (
                        event.decoded("DTEND") if "DTEND" in event else ""
                    ) + LOCAL_TIMEZONE
                    if (not_started and now >= normalize_date(start)) or (
                        not_ended and now >= normalize_date(end)
                    ):
                        continue

                    conversions = {
                        "UID": "uid",
                        "DTSTAMP": "dumb_timestamp",
                        "SUMMARY": "title",
                        "LOCATION": "location",
                        "DESCRIPTION": "description",
                        "ACTION": "action",
                        "LAST-MODIFIED": "modified",
                        "CREATED": "created",
                        "TRANSP": "transparency",
                        "STATUS": "status",
                        "SEQUENCE": "times_updated",
                    }

                    pevent = {}
                    pevent["start"] = start
                    pevent["end"] = end

                    for item in event.items():
                        if item[0] in conversions:
                            pevent[conversions[item[0]]] = event.decoded(item[0])

                    data["events"].append(pevent)

            return Response(data)
        else:
            return Response(
                ["This endpoint is a WIP you should not get this response when it's ready."]
            )


class StatusViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        return JsonResponse({"status": "UP"})
