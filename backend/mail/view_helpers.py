import datetime
from typing import TypedDict

import requests
from icalendar import Calendar
from .timed_cache import SingleValueTimedCache
from django.conf import settings
from django.utils.safestring import mark_safe

import nh3


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
    allowed_tags = set(nh3.ALLOWED_TAGS) | {
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
        **nh3.ALLOWED_ATTRIBUTES,
        "a": {"href", "target"},
    }

    sanitized_content = nh3.clean(
        content,
        tags=allowed_tags,
        attributes=allowed_attributes,
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
        subject (str): The subject field of the email.
        force_fetch (bool): Whether to force fetching events from the calendar.
    """
    safe_content = mark_safe(_sanitize_html(content))
    safe_info_chief_content = mark_safe(_sanitize_html(info_chief_content))

    event_list = events_cache.get()
    if event_list is None or force_fetch:
        event_list = _fetch_events()
        events_cache.set(event_list)
    assert event_list is not None

    return {
        "week_number": week_number(),
        "events": event_list,
        "content": safe_content,
        "info_chief_content": safe_info_chief_content,
        "website_url": settings.INFO_DSEKTIONEN_WEBSITE_URL,
        "info_email": settings.INFO_DSEKTIONEN_INFO_EMAIL,
        "gdpr_url": settings.INFO_DSEKTIONEN_GDPR_URL,
        "logo_url": settings.INFO_DSEKTIONEN_LOGO_URL,
        "unsubscribe_url": settings.INFO_DSEKTIONEN_UNSUBSCRIBE_URL,
        "instagram_url": settings.INFO_DSEKTIONEN_INSTAGRAM_URL,
        "facebook_url": settings.INFO_DSEKTIONEN_FACEBOOK_URL,
        "facebook_group_url": settings.INFO_DSEKTIONEN_FACEBOOK_GROUP_URL,
        "more_social_media_url": settings.INFO_DSEKTIONEN_MORE_SOCIAL_MEDIA_URL,
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

    # Fetch the iCal calendar data from the configured URL
    response = requests.get(settings.INFO_CALENDAR_ICAL_URL)
    assert response.ok, "Failed to fetch calendar data"

    # Parse the iCal data and extract all VEVENT components
    calendar = Calendar.from_ical(response.text)
    events = [c for c in calendar.walk() if c.name == "VEVENT"]

    def to_datetime(dt):
        """Convert iCal datetime/date object to timezone-aware datetime."""
        # Extract the actual date/datetime value
        d = dt.dt if hasattr(dt, "dt") else dt

        # Convert date-only objects to datetime at midnight UTC
        if isinstance(d, datetime.date) and not isinstance(d, datetime.datetime):
            d = datetime.datetime.combine(d, datetime.time.min)

        # Ensure timezone awareness (assume UTC if not specified)
        if d.tzinfo is None:
            d = d.replace(tzinfo=datetime.timezone.utc)

        return d

    def format_date_only(dt):
        """Format datetime as date without time: '25 December'"""
        return dt.strftime("%d %B")

    def format_datetime(dt):
        """Format datetime with time: '25 December 14:00'"""
        return dt.strftime("%d %B %H:%M")

    def format_time_only(dt):
        """Format just the time: '14:00'"""
        return dt.strftime("%H:%M")

    def format_date_range(start_dt, end_dt):
        """Format date string based on event type and duration."""
        # Check if this is a whole-day event (starts and ends at midnight)
        is_whole_day_event = (
            end_dt
            and start_dt.time() == datetime.time(0, 0)
            and end_dt.time() == datetime.time(0, 0)
            and end_dt > start_dt
        )

        if is_whole_day_event:
            # Calculate duration in days
            days = (end_dt - start_dt).days

            if days == 1:
                # Single whole-day event: "25 December"
                return format_date_only(start_dt)
            elif days > 1:
                # Multi-day whole-day event: "25 December - 27 December"
                # Subtract 1 day from end because iCal whole-day events are exclusive
                last_day = end_dt - datetime.timedelta(days=1)
                return f"{format_date_only(start_dt)} - {format_date_only(last_day)}"
            else:
                # Fallback case (shouldn't normally happen)
                return f"{format_datetime(start_dt)}<br>{format_datetime(end_dt)}"

        elif end_dt and start_dt.date() == end_dt.date():
            # Same-day event with time: "25 December 14:00 - 16:00"
            return f"{format_datetime(start_dt)} - {format_time_only(end_dt)}"

        elif end_dt:
            # Multi-day event with specific times: "25 December 14:00<br>27 December 16:00"
            return f"{format_datetime(start_dt)}<br>{format_datetime(end_dt)}"

        else:
            # Event without end time: "25 December 14:00"
            return format_datetime(start_dt) if start_dt else ""

    # Sort all events by start time (earliest first)
    # Events without start time are sorted to the end
    events.sort(
        key=lambda e: to_datetime(e.get("dtstart"))
        if e.get("dtstart")
        else datetime.datetime.max.replace(tzinfo=datetime.timezone.utc)
    )

    # Filter to only include events that haven't started yet
    now = datetime.datetime.now(datetime.timezone.utc)
    upcoming_events = [
        e for e in events if "dtstart" in e and to_datetime(e["dtstart"]) >= now
    ]

    # Process the first 5 upcoming events
    result: list[EventDict] = []
    for event in upcoming_events[:5]:
        start_dt = to_datetime(event.get("dtstart"))
        end_dt = to_datetime(event.get("dtend")) if event.get("dtend") else None

        # Format the date string and add to results
        date_str = format_date_range(start_dt, end_dt)
        title = _sanitize_html(event.get("summary", ""))
        result.append({"title": title, "date": date_str})

    return result
