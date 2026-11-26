import asyncio
import django
from django.conf import settings
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler
from django.db import connections

import socketio
from .sockets import sio
from .admission import HTTPConcurrencyMiddleware
from .handlers import SyncMiddlewareASGIHandler

django.setup(set_prefix=False)
django_asgi_app = SyncMiddlewareASGIHandler()
# application = socketio.ASGIApp(sio, django_asgi_app, socketio_path="ws")


def _run_periodic_command(name, **options):
    """Release ORM connections opened by a command in its worker thread."""
    from django.core.management import call_command

    try:
        call_command(name, **options)
    finally:
        connections.close_all()


# # ! This should be changed. This runs once per worker, so if we have multiple workers, we'll have multiple periodic tasks running.
async def _send_queued_mail_periodically():
    """Send queued mail every 10 seconds, mirroring the old uWSGI timer."""
    while True:
        try:
            await asyncio.to_thread(
                _run_periodic_command, "send_queued_mail", processes=1
            )
        except Exception as e:
            print(f"send_queued_mail failed: {e}")
        await asyncio.sleep(10)


async def _clear_old_events_periodically():
    """Clear old events every 24 hours, mirroring the old uWSGI timer."""
    while True:
        try:
            await asyncio.to_thread(_run_periodic_command, "nightly")
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


if settings.SETTINGS_MODULE == "backend.app.settings_development":
    django_asgi_app = ASGIStaticFilesHandler(django_asgi_app)

django_asgi_app = HTTPConcurrencyMiddleware(
    django_asgi_app, settings.ASGI_HTTP_CONCURRENCY
)

application = LifespanMiddleware(
    socketio.ASGIApp(sio, django_asgi_app, socketio_path="/ws")
)
