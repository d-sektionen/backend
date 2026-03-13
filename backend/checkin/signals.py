from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Doorkeeper
import asyncio
from backend.app.sockets import sio


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
        print(f"Emitting new_doorkeeper with data: {data}")
        print(f"Emitting to room: event_doorkeepers_{instance.event.id}")
        asyncio.run(
            sio.emit(
                "new_doorkeeper",
                data,
                room=f"event_doorkeepers_{instance.event.id}",
            )
        )


@receiver(post_delete, sender=Doorkeeper)
def doorkeeper_deleted(sender, instance, **kwargs):
    data = {
        "doorkeeper_id": instance.id,
        "event_id": instance.event.id,
    }
    print(f"Emitting delete_doorkeeper with data: {data}")
    print(f"Emitting to room: event_doorkeepers_{instance.event.id}")
    asyncio.run(
        sio.emit(
            "delete_doorkeeper",
            data,
            room=f"event_doorkeepers_{instance.event.id}",
        )
    )
