import requests
from django.utils import timezone
from .models import Webhook


def notify_webhook_unconfirmed_booking(booking_data, is_updated):
    """Send notification to hook with info of an unconfirmed booking.

    Args:
        booking_data: Data from the booking, either model or serializer.
        is_updated: If an existing booking is being updated.
    """

    hook = booking_data.get("item").webhook

    if hook is None:
        return

    user_fullname = (
        f"{booking_data.get('user').first_name} {booking_data.get('user').last_name}"
    )
    start = booking_data.get("start").strftime("*%d/%m %H:%M*")
    end = booking_data.get("end").strftime("*%d/%m %H:%M*")

    # Calculate the duration until the booking
    duration_until = booking_data.get("start") - timezone.now()
    dur_hours = duration_until.seconds // (60 * 60)
    dur_minutes = (duration_until.seconds // 60) % 60

    restricted_emoji = (
        ":white_check_mark:" if booking_data.get("restricted_timeslot") else ":x:"
    )

    content = f":calendar: **bokningsnotifikation till** *{hook.name}*\n"

    if is_updated:
        content += "**Uppdaterad bokning:**\n"
    else:
        content += "**Ny bokning:**\n"

    content += (
        "Bekräftad: :x:\n"
        f"Begränsad tidsperiod: {restricted_emoji}\n"
        f"Objekt *{booking_data.get('item').name}* "
        f"bokades av *{user_fullname}* (*{booking_data.get('user')}*) "
        f"mellan {start} - {end} (Startar om {duration_until.days}d {dur_hours}t {dur_minutes}m)\n"
        f"Ändamål: {booking_data.get('description')}\n"
    )

    notify_webhook(hook, content)


def notify_webhook(hook: Webhook, message: str) -> None:
    """Send a message to a webhook

    Args:
        hook: the webhook to notify
        content: Content to include in the message.
    """

    data = {}

    match hook.service:
        case "discord":
            data = {"content": message}
        case "slack":
            data = {"text": message}
        case _:
            raise Exception(f"Unknown webhook service type ({hook.service})")

    requests.post(hook.url, json=data)
