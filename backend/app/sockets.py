# backend/app/sockets.py
import asyncio
import socketio
import logging

logger = logging.getLogger(__name__)


def _create_server():
    from django.conf import settings

    cors_origins = getattr(settings, "CORS_ALLOWED_ORIGINS", [])
    return socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=cors_origins)


sio = _create_server()


@sio.event
async def connect(sid, environ):
    from django.http import HttpRequest
    from backend.oauth2.auth import CookieJWTAuthentication

    request = HttpRequest()
    cookies = environ.get("HTTP_COOKIE", "")
    for cookie in cookies.split(";"):
        cookie = cookie.strip()
        if cookie.startswith("access_token="):
            request.COOKIES["access_token"] = cookie.split("=", 1)[1]
            break

    result = await asyncio.to_thread(CookieJWTAuthentication().authenticate, request)

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
