# backend/app/sockets.py
import asyncio
import socketio
import logging
from asgiref.sync import async_to_sync
from django.conf import settings

logger = logging.getLogger(__name__)


def _create_server():
    cors_origins = getattr(settings, "CORS_ALLOWED_ORIGINS", [])
    manager = socketio.AsyncRedisManager(settings.REDIS_URL)
    return socketio.AsyncServer(
        async_mode="asgi",
        cors_allowed_origins=cors_origins,
        client_manager=manager,
        transports=["websocket"],
    )


sio = _create_server()
# WebSocket authentication also uses the ORM, outside Django's HTTP lifecycle.
# Bound it separately and release its connection before accepting the socket.
_authentication_slots = asyncio.Semaphore(settings.ASGI_HTTP_CONCURRENCY)


def _authenticate_socket(request):
    from django.db import connections
    from backend.oauth2.auth import CookieJWTAuthentication

    try:
        return CookieJWTAuthentication().authenticate(request)
    finally:
        connections.close_all()


@sio.event
async def connect(sid, environ):
    from django.http import HttpRequest

    request = HttpRequest()
    cookies = environ.get("HTTP_COOKIE", "")
    for cookie in cookies.split(";"):
        cookie = cookie.strip()
        if cookie.startswith("access_token="):
            request.COOKIES["access_token"] = cookie.split("=", 1)[1]
            break

    async with _authentication_slots:
        result = await asyncio.to_thread(_authenticate_socket, request)

    if result is None:
        logger.warning(f"Connection rejected, authentication failed: {sid}")
        return False

    user, token = result
    logger.debug(f"Client connected: {sid} (user={user.username})")
    await sio.save_session(sid, {"user_id": user.id, "username": user.username})


@sio.event
async def disconnect(sid):
    logger.debug(f"Client disconnected: {sid}")


@sio.event
async def join(sid, data):
    logger.debug(f"Client {sid} joining room: {data['room']}")
    await sio.enter_room(sid, data["room"])


@sio.event
async def leave(sid, data):
    logger.debug(f"Client {sid} leaving room: {data['room']}")
    await sio.leave_room(sid, data["room"])


@sio.event
async def ping(sid, data):
    logger.debug(f"Received ping from {sid}: {data}")
    await sio.emit("pong", {"message": "pong"}, to=sid)


def emit_event(
    event: str,
    data: dict,
    room: str | None = None,
    namespace: str | None = None,
    timeout: float | None = None,
):
    """
    Sync-safe Socket.IO emit wrapper for Django signals / ORM hooks.
    """

    async def emit():
        async with asyncio.timeout(timeout):
            await sio.emit(event, data, room=room, namespace=namespace)

    async_to_sync(emit)()
