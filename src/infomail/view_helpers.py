import requests
from icalendar import Calendar, Event
from datetime import datetime, timedelta

CAL_URL = "http://kalender.d-sektionen.se"

def eventData(state):
    res = requests.get(CAL_URL)
    ical_string = res.text

    cal = Calendar.from_ical(ical_string)
    now = datetime.now()
    now_plus_21_days = now + timedelta(days=21)

    events = []
    for component in cal.walk():
        if component.name == "VEVENT":
            event = Event(component)
            start = event.get('dtstart').dt
            end = event.get('dtend').dt

            if end >= now and start <= now_plus_21_days:
                events.append({
                    'summary': event.get('summary'),
                    'start': start.isoformat(),
                    'end': end.isoformat()
                })

    events.sort(key=lambda x: x['start'])
    state.add_events(events)
