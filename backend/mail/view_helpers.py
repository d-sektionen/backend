import datetime
from typing import TypedDict

import requests
from icalendar import Calendar
from .timed_cache import SingleValueTimedCache


# TODO: replace this with the one from settings
CALENDAR_URL = "https://calendar.google.com/calendar/ical/c_93a709266d679561caf5bcc20fb621fb0af75dd7d6e78c568b65fec39fc34e3b%40group.calendar.google.com/public/basic.ics"


class EventDict(TypedDict):
    title: str
    date: str


def week_number() -> int:
    return datetime.date.today().isocalendar()[0]


def fetch_events() -> list[EventDict]:
    # Extract and format up to 5 upcoming events from the iCal calendar
    response = requests.get(CALENDAR_URL)
    calendar = Calendar.from_ical(response.content)
    events = [c for c in calendar.walk() if c.name == "VEVENT"]

    def to_datetime(dt):
        d = dt.dt if hasattr(dt, "dt") else dt
        if isinstance(d, datetime.date) and not isinstance(d, datetime.datetime):
            d = datetime.datetime.combine(
                d, datetime.time.min, tzinfo=datetime.timezone.utc
            )
        if d.tzinfo is None:
            d = d.replace(tzinfo=datetime.timezone.utc)
        return d

    # Sort events by start datetime, earliest first
    events.sort(
        key=lambda e: to_datetime(e.get("dtstart"))
        if e.get("dtstart")
        else datetime.datetime.max.replace(tzinfo=datetime.timezone.utc)
    )

    now = datetime.datetime.now(datetime.timezone.utc)
    upcoming_events = [
        e for e in events if "dtstart" in e and to_datetime(e["dtstart"]) >= now
    ]

    result: list[EventDict] = []
    for event in upcoming_events[:5]:
        start_dt = to_datetime(event.get("dtstart"))
        end_dt = to_datetime(event.get("dtend")) if event.get("dtend") else None

        # Check for whole-day event (start and end at 00:00, duration is multiple of 24h)
        if (
            end_dt
            and start_dt.time() == datetime.time(0, 0)
            and end_dt.time() == datetime.time(0, 0)
            and end_dt > start_dt
        ):
            days = (end_dt - start_dt).days
            if days == 1:
                # Single whole day event
                date_str = start_dt.strftime("%d %B")
            elif days > 1:
                # Multi-day whole day event
                date_str = f"{start_dt.strftime('%d %B')} - {(end_dt - datetime.timedelta(days=1)).strftime('%d %B')}"
            else:
                # Fallback to default formatting
                date_str = f"{start_dt.strftime('%d %B %H:%M')}<br>{end_dt.strftime('%d %B %H:%M')}"
        elif end_dt and start_dt.date() == end_dt.date():
            date_str = (
                f"{start_dt.strftime('%d %B %H:%M')} - {end_dt.strftime('%H:%M')}"
            )
        elif end_dt:
            date_str = f"{start_dt.strftime('%d %B %H:%M')}<br>{end_dt.strftime('%d %B %H:%M')}"
        else:
            date_str = start_dt.strftime("%d %B %H:%M") if start_dt else ""

        title = event.get("summary", "")
        result.append({"title": title, "date": date_str})

    return result


events_cache = SingleValueTimedCache[list[EventDict]]()


def get_events(force_fetch: bool = False) -> list[EventDict]:
    event_list = events_cache.get()
    if events_cache.get() is None or force_fetch:
        event_list = fetch_events()
        events_cache.set(event_list)
    return event_list
