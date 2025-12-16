import datetime
from typing import TypedDict

import requests
from icalendar import Calendar
from .timed_cache import SingleValueTimedCache
from django.conf import settings
from django.utils.safestring import mark_safe

import bleach


class EventDict(TypedDict):
    title: str
    date: str


def _sanitize_html(content: str) -> str:
    """Sanitize HTML content to allow only a safe subset of tags and attributes.
    Args:
        content (str): The HTML content to sanitize.
    Returns:
        str: The sanitized HTML content.
    """
    allowed_tags = set(bleach.sanitizer.ALLOWED_TAGS) | {
        "h1",
        "h2",
        "h3",
        "p",
        "br",
        "strong",
        "em",
        "u",
        "ul",
        "ol",
        "li",
        "a",
    }

    allowed_attributes = {
        **bleach.sanitizer.ALLOWED_ATTRIBUTES,
        "a": ["href", "target", "rel"],
    }

    sanitized_content = bleach.clean(
        content,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True,
    )
    return sanitized_content


events_cache = SingleValueTimedCache[list[EventDict]]()


def generate_mail_context(
    content: str,
    info_chief_content: str,
    subject: str = "Infomail",
    force_fetch: bool = False,
) -> dict:
    """Generate context for the newsletter email template.
    Args:
        content (str): The main content of the newsletter.
        info_chief_content (str): The content from the info chief.
        subject (str): The subject feild of the email.
        force_fetch (bool): Whether to force fetching events from the calendar.
    """
    safe_content = mark_safe(_sanitize_html(content))
    safe_info_chief_content = mark_safe(_sanitize_html(info_chief_content))

    event_list = events_cache.get()
    if events_cache.get() is None or force_fetch:
        event_list = _fetch_events()
        events_cache.set(event_list)
    assert event_list is not None

    return {
        "week_number": week_number(),
        "events": event_list,
        "content": safe_content,
        "info_chief_content": safe_info_chief_content,
        "website_url": settings.INFO_D_SEKTIONEN_WEBSITE_URL,
        "info_email": settings.INFO_D_SEKTIONEN_INFO_EMAIL,
        "gdpr_url": settings.INFO_D_SEKTIONEN_GDPR_URL,
        "logo_url": settings.INFO_D_SEKTIONEN_LOGO_URL,
        "unsubscribe_url": settings.INFO_D_SEKTIONEN_UNSUBSCRIBE_URL,
        "instagram_url": settings.INFO_D_SEKTIONEN_INSTAGRAM_URL,
        "facebook_url": settings.INFO_D_SEKTIONEN_FACEBOOK_URL,
        "facebook_group_url": settings.INFO_D_SEKTIONEN_FACEBOOK_GROUP_URL,
        "more_social_media_url": settings.INFO_D_SEKTIONEN_MORE_SOCIAL_MEDIA_URL,
        "calendar_url": settings.INFO_CALENDAR_ICAL_URL,
        "subject": subject,
    }


def week_number() -> int:
    """Get the current ISO week number."""
    return datetime.date.today().isocalendar()[1]


def _fetch_events() -> list[EventDict]:
    """Fetch and process upcoming events from the iCal calendar.
    Returns:
        list[EventDict]: A list of upcoming events with title and formatted date."""
    # Extract and format up to 5 upcoming events from the iCal calendar
    response = requests.get(settings.INFO_CALENDAR_ICAL_URL)

    calendar = Calendar.from_ical(response.text)
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
