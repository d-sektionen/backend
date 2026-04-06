# backend/app/sockets.py
import socketio
import logging

logger = logging.getLogger(__name__)

sio = socketio.AsyncServer(
    async_mode="asgi", cors_allowed_origins=["http://localhost:4000"]
)


@sio.event
async def connect(sid, environ):
    logger.debug(f"Client connected: {sid}")


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
