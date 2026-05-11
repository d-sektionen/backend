from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Doorkeeper
from backend.app.sockets import emit_event


@receiver(post_save, sender=Doorkeeper)
def new_doorkeeper(sender, instance, created, **kwargs):
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
            "event": {
                "id": instance.event.id,
                "name": instance.event.name,
                "archived": instance.event.archived,
                "actions": instance.event.ACTIONS,
                "status_message": instance.event.get_status_message(),
            },
        }
        emit_event(
            "new_doorkeeper",
            data,
            room=f"event_doorkeepers_{instance.event.id}",
        )


@receiver(post_delete, sender=Doorkeeper)
def doorkeeper_deleted(sender, instance, **kwargs):
    data = {
        "doorkeeper_id": instance.id,
        "event_id": instance.event.id,
    }

    emit_event(
        "delete_doorkeeper",
        data,
        room=f"event_doorkeepers_{instance.event.id}",
    )
