from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import SpeakerRequest, Attendant
import asyncio
from backend.app.sockets import sio


@receiver(post_save, sender=SpeakerRequest)
def user_created(sender, instance, created, **kwargs):
    if created:
        speaker = {
            "id": instance.id,
            "user": {
                "id": instance.user.id,
                "username": instance.user.username,
                "first_name": instance.user.first_name,
                "last_name": instance.user.last_name,
                "pretty_name": instance.user.get_full_name(),
            },
            "prioritized": instance.prioritized,
        }
        asyncio.run(
            sio.emit(
                "new_speaker_request",
                {
                    "speaker": speaker,
                    "meeting_id": instance.meeting.id,
                },
                room=f"meeting_speker_{instance.meeting.id}",
            )
        )


@receiver(post_delete, sender=SpeakerRequest)
def speaker_request_deleted(sender, instance, **kwargs):
    asyncio.run(
        sio.emit(
            "delete_speaker_request",
            {
                "speaker_request_id": instance.id,
                "meeting_id": instance.meeting.id,
            },
            room=f"meeting_speker_{instance.meeting.id}",
        )
    )


@receiver(post_save, sender=Attendant)
def new_attendant(sender, instance, created, **kwargs):
    if created:
        data = {
            "id": instance.id,
            "user": {
                "id": instance.user.id,
                "username": instance.user.username,
                "first_name": instance.user.first_name,
                "last_name": instance.user.last_name,
                "pretty_name": instance.user.get_full_name(),
            },
            "has_voting_rights": instance.has_voting_rights,
            "meeting_id": instance.meeting.id,
        }

        asyncio.run(
            sio.emit(
                "new_attendant",
                data,
                room=f"meeting_attendants_{instance.meeting.id}",
            )
        )


@receiver(post_delete, sender=Attendant)
def attendant_deleted(sender, instance, **kwargs):
    asyncio.run(
        sio.emit(
            "delete_attendant",
            {
                "attendant_id": instance.id,
                "meeting_id": instance.meeting.id,
            },
            room=f"meeting_attendants_{instance.meeting.id}",
        )
    )
