import asyncio
from django.core.asgi import get_asgi_application

import socketio
from .sockets import sio

django_asgi_app = get_asgi_application()
# application = socketio.ASGIApp(sio, django_asgi_app, socketio_path="ws")


# # ! This should be changed. This runs once per worker, so if we have multiple workers, we'll have multiple periodic tasks running.
async def _send_queued_mail_periodically():
    """Send queued mail every 10 seconds, mirroring the old uWSGI timer."""
    from django.core.management import call_command

    while True:
        try:
            await asyncio.to_thread(call_command, "send_queued_mail", processes=1)
        except Exception as e:
            print(f"send_queued_mail failed: {e}")
        await asyncio.sleep(10)


async def _clear_old_events_periodically():
    """Clear old events every 24 hours, mirroring the old uWSGI timer."""
    from django.core.management import call_command

    while True:
        try:
            await asyncio.to_thread(call_command, "nightly")
        except Exception as e:
            print(f"nightly command failed: {e}")
        await asyncio.sleep(24 * 60 * 60)  # Sleep for 24 hours


class LifespanMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "lifespan":
            event = await receive()
            if event["type"] == "lifespan.startup":
                asyncio.ensure_future(_send_queued_mail_periodically())
                asyncio.ensure_future(_clear_old_events_periodically())
                await send({"type": "lifespan.startup.complete"})
            event = await receive()
            if event["type"] == "lifespan.shutdown":
                await send({"type": "lifespan.shutdown.complete"})
        else:
            await self.app(scope, receive, send)


application = LifespanMiddleware(
    socketio.ASGIApp(sio, django_asgi_app, socketio_path="/ws")
)
