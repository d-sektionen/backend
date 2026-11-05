import logging
from contextlib import contextmanager
from contextvars import ContextVar

from django.db import transaction
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import SpeakerRequest, Attendant, Vote, Alternative

from backend.app.sockets import emit_event

logger = logging.getLogger(__name__)
_publication_batch = ContextVar("meeting_publication_batch", default=None)


@contextmanager
def batch_notifications():
    """Stop retrying a failed transport for the rest of one bulk operation.

    Each notification still uses on_commit so nested rollbacks discard it. The
    failure flag expires with this operation; no worker-wide outage cache.
    """
    if _publication_batch.get() is not None:
        yield
        return
    token = _publication_batch.set({"failed": False})
    try:
        yield
    finally:
        _publication_batch.reset(token)


def _publish_event(event, data, room):
    # Publication cannot roll back a committed vote. Never log voter/choice data.
    try:
        # Redis reconnect backoff must not hold an accepted vote's HTTP slot.
        emit_event(event, data, room=room, timeout=1.0)
        return True
    except Exception:
        logger.warning("Meeting notification failed; clients can refresh state")
        return False


def _queue_event(event, data, room):
    batch = _publication_batch.get()

    def publish():
        if batch is not None and batch["failed"]:
            return
        if not _publish_event(event, data, room) and batch is not None:
            batch["failed"] = True

    transaction.on_commit(publish)


def queue_alternative_update(alternative_id, text, vote_id, meeting_id):
    data = {"id": alternative_id, "text": text, "vote": vote_id, "meeting": meeting_id}
    room = f"meeting_votes_{meeting_id}"
    _queue_event("update_alternative", data, room)


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
        emit_event(
            "new_speaker_request",
            {
                "speaker": speaker,
                "meeting_id": instance.meeting.id,
            },
            room=f"meeting_speaker_{instance.meeting.id}",
        )


@receiver(post_delete, sender=SpeakerRequest)
def speaker_request_deleted(sender, instance, **kwargs):
    data = {"speaker_request_id": instance.id, "meeting_id": instance.meeting_id}
    room = f"meeting_speaker_{instance.meeting_id}"
    _queue_event("delete_speaker_request", data, room)


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
            "meeting_id": instance.meeting_id,
        }
        room = f"meeting_attendants_{instance.meeting_id}"
        _queue_event("new_attendant", data, room)


@receiver(post_delete, sender=Attendant)
def attendant_deleted(sender, instance, **kwargs):
    data = {"attendant_id": instance.id, "meeting_id": instance.meeting_id}
    room = f"meeting_attendants_{instance.meeting_id}"
    _queue_event("delete_attendant", data, room)


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
        emit_event(
            "new_vote",
            data,
            room=f"meeting_votes_{instance.meeting.id}",
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

        emit_event(
            "new_vote",
            data,
            room=f"meeting_votes_{instance.meeting.id}",
        )

    else:
        data = {
            "id": instance.id,
            "meeting": instance.meeting.id,
        }

        emit_event(
            "delete_vote",
            data,
            room=f"meeting_votes_{instance.meeting.id}",
        )


@receiver(post_delete, sender=Vote)
def vote_deleted(sender, instance, **kwargs):
    data = {
        "id": instance.id,
        "meeting": instance.meeting.id,
    }

    emit_event(
        "delete_vote",
        data,
        room=f"meeting_votes_{instance.meeting.id}",
    )


@receiver(post_delete, sender=Alternative)
def alternative_deleted(sender, instance, **kwargs):
    data = {
        "id": instance.id,
        "vote": instance.vote.id,
        "meeting": instance.vote.meeting.id,
    }

    emit_event(
        "delete_alternative",
        data,
        room=f"meeting_votes_{instance.vote.meeting.id}",
    )


@receiver(post_save, sender=Alternative)
def alternative_updated(sender, instance, created, **kwargs):
    if not instance.vote.open:
        return

    if not created:
        queue_alternative_update(
            instance.pk, instance.text, instance.vote_id, instance.vote.meeting_id
        )

    else:
        data = {
            "id": instance.id,
            "text": instance.text,
            "vote": instance.vote.id,
            "meeting": instance.vote.meeting.id,
        }

        emit_event(
            "new_alternative",
            data,
            room=f"meeting_votes_{instance.vote.meeting.id}",
        )
