from django.conf import settings
from django.utils import timezone
import requests

def notify_werk_of_booking(booking_data, is_confirmed):
    """Send notification to Werk with info of a booking.

    Args:
        booking_data: Data from the booking, either model or serializer.
        is_confirmed: If the booking is confirmed or not.
    """
    user_fullname = f"{booking_data.get('user').first_name} {booking_data.get('user').last_name}"
    start = booking_data.get('start').strftime("%Y/%m/*%d %H:%M*")
    end = booking_data.get('end').strftime("%Y/%m/*%d %H:%M*")
    
    # Calculate the duration until the booking
    duration_until = booking_data.get('start') - timezone.now()
    dur_hours = duration_until.seconds // (60*60)
    dur_minutes = (duration_until.seconds // 60) % 60

    confirmed_emoji = ":white_check_mark:" if is_confirmed else ":x:"
    content = ("*Ny bokning:*\n"
               f"Bekräftad: {confirmed_emoji}\n"
               f"Objekt: *{booking_data.get('item').name}*\n"
               f"Bokades av: *{user_fullname}* ({booking_data.get('user')})\n"
               f"Mellan: {start} - {end} (Startar om {duration_until.days}d {dur_hours}t {dur_minutes}m)\n"
               f"Ändamål: {booking_data.get('description')}\n"
               "----------------------------------------------")

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
