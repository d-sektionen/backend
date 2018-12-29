from rest_framework.decorators import api_view
from rest_framework.response import Response
from icalendar import Calendar, Event, vDatetime
from datetime import timedelta

import requests

# move to settings if you cba.
CAL_URL = 'https://calendar.google.com/calendar/ical/webmaster%40d.lintek.liu.se/public/basic.ics'
LOCAL_TIMEZONE = timedelta(hours=2)

"""
WIP
Parses the D-sektionen calendar and creates a Django REST Framework endpoint for it.

Inspiration from https://github.com/bsab/icstojson/blob/master/app.py
"""
@api_view()
def section_calendar(request):
  r = requests.get(CAL_URL)
  if r.status_code == 200:
    cal = Calendar.from_ical(r.text)
    data = {}
    data[cal.name] = dict(cal.items())
    data[cal.name]['VEVENT'] = []

    for event in cal.walk():
        if isinstance(event, Event):

            uid = event.decoded("UID") if "UID" in event else ""
            dtstamp = event.decoded("DTSTAMP") if "DTSTAMP" in event else ""
            start = (event.decoded("DTSTART") if "DTSTART" in event else "") + LOCAL_TIMEZONE
            end = (event.decoded("DTEND") if "DTEND" in event else "") + LOCAL_TIMEZONE
            title = event.decoded("SUMMARY") if "SUMMARY" in event else ""
            track = event.decoded("LOCATION") if "LOCATION" in event else ""
            description = event.decoded("DESCRIPTION") if "DESCRIPTION" in event else ""
            action = event.decoded("ACTION") if "ACTION" in event else ""

            pevent = {}
            pevent["DTSTAMP"]= dtstamp
            pevent["UID"]= uid
            pevent["CLASS"] = "PUBLIC"
            pevent["title"] = title
            pevent["location"] = track
            pevent["ACTION"] = action
            pevent["start"] = start #vDatetime(start).to_ical() # start.time().strftime("%Y%m%dT%H%M")
            # pevent["GEO"]= ""
            pevent["description"] = description
            pevent["end"] = end #vDatetime(end).to_ical() #end.time().strftime("%Y%m%dT%H%M")

            data[cal.name]['VEVENT'].append(pevent)
    return Response(data)
  else:
    return Response(['This endpoint is a WIP you should not get this response when it\'s ready.'])