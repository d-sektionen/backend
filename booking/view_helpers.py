from django.conf import settings
from django.utils import timezone
import requests


def notify_werk_unconfirmed_booking(booking_data, is_updated):
    """Send notification to Werk with info of an unconfirmed booking.

    Args:
        booking_data: Data from the booking, either model or serializer.
        is_updated: If an existing booking is being updated.
    """
    user_fullname = f"{booking_data.get('user').first_name} {booking_data.get('user').last_name}"
    start = booking_data.get("start").strftime("*%d/%m %H:%M*")
    end = booking_data.get("end").strftime("*%d/%m %H:%M*")

    # Calculate the duration until the booking
    duration_until = booking_data.get("start") - timezone.now()
    dur_hours = duration_until.seconds // (60 * 60)
    dur_minutes = (duration_until.seconds // 60) % 60

    restricted_emoji = ":white_check_mark:" if booking_data.get("restricted_timeslot") else ":x:"

    content = "*Uppdaterad bokning:*\n" if is_updated else "*Ny bokning:*\n"
    content += (
        "Bekräftad: :x:\n"
        f"Begränsad tidsperiod: {restricted_emoji}\n"
        f"Objekt *{booking_data.get('item').name}* "
        f"bokades av *{user_fullname}* (*{booking_data.get('user')}*) "
        f"mellan {start} - {end} (Startar om {duration_until.days}d {dur_hours}t {dur_minutes}m)\n"
        f"Ändamål: {booking_data.get('description')}\n"
    )

    try:
        notify_werk(content)
    except:
        print("Could not send booking notification to werk.")


def notify_werk(content):
    """Notify work through a webhook to their slack.

    Args:
        content: Content to include in the message.
    """
    if settings.WERK_WEBHOOK_URL != "":
        requests.post(settings.WERK_WEBHOOK_URL, json={"text": content})
