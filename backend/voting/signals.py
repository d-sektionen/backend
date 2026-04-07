from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import SpeakerRequest, Attendant, Vote, Alternative
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
                room=f"meeting_speaker_{instance.meeting.id}",
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
            room=f"meeting_speaker_{instance.meeting.id}",
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


@receiver(post_save, sender=Vote)
def new_vote(sender, instance, created, **kwargs):
    if created:
        if not instance.open:
            return

        data = {
            "id": instance.id,
            "meeting": instance.meeting.id,
            "open": instance.open,
            "question": instance.question,
        }
        alternativesRaw = Alternative.objects.filter(vote=instance)
        alternatives = []
        for alt in alternativesRaw:
            alternatives.append(
                {
                    "id": alt.id,
                    "text": alt.text,
                }
            )
        data["alternatives"] = alternatives

        asyncio.run(
            sio.emit(
                "new_vote",
                data,
                room=f"meeting_votes_{instance.meeting.id}",
            )
        )

    elif instance.open:
        data = {
            "id": instance.id,
            "open": instance.open,
            "meeting": instance.meeting.id,
            "question": instance.question,
        }

        alternativesRaw = Alternative.objects.filter(vote=instance)
        alternatives = []
        for alt in alternativesRaw:
            alternatives.append(
                {
                    "id": alt.id,
                    "text": alt.text,
                }
            )
        data["alternatives"] = alternatives

        asyncio.run(
            sio.emit(
                "new_vote",
                data,
                room=f"meeting_votes_{instance.meeting.id}",
            )
        )

    else:
        data = {
            "id": instance.id,
            "meeting": instance.meeting.id,
        }
        print("Emitting delete_vote for vote id:", instance.id)
        asyncio.run(
            sio.emit(
                "delete_vote",
                data,
                room=f"meeting_votes_{instance.meeting.id}",
            )
        )


@receiver(post_delete, sender=Vote)
def vote_deleted(sender, instance, **kwargs):
    data = {
        "id": instance.id,
        "meeting": instance.meeting.id,
    }

    asyncio.run(
        sio.emit(
            "delete_vote",
            data,
            room=f"meeting_votes_{instance.meeting.id}",
        )
    )


@receiver(post_delete, sender=Alternative)
def alternative_deleted(sender, instance, **kwargs):
    data = {
        "id": instance.id,
        "vote": instance.vote.id,
        "meeting": instance.vote.meeting.id,
    }

    asyncio.run(
        sio.emit(
            "delete_alternative",
            data,
            room=f"meeting_votes_{instance.vote.meeting.id}",
        )
    )


@receiver(post_save, sender=Alternative)
def alternative_updated(sender, instance, created, **kwargs):
    if not instance.vote.open:
        return

    if not created:
        data = {
            "id": instance.id,
            "text": instance.text,
            "vote": instance.vote.id,
            "meeting": instance.vote.meeting.id,
        }

        asyncio.run(
            sio.emit(
                "update_alternative",
                data,
                room=f"meeting_votes_{instance.vote.meeting.id}",
            )
        )

    else:
        data = {
            "id": instance.id,
            "text": instance.text,
            "vote": instance.vote.id,
            "meeting": instance.vote.meeting.id,
        }

        asyncio.run(
            sio.emit(
                "new_alternative",
                data,
                room=f"meeting_votes_{instance.vote.meeting.id}",
            )
        )
