import os
import socketio
from django.core.asgi import get_asgi_application

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=["http://localhost:4000"],
)

django_asgi_app = get_asgi_application()

application = socketio.ASGIApp(
    sio,
    django_asgi_app,
    socketio_path="/socket",
)


@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")


@sio.event
async def join(sid, data):
    room = data["room"]
    await sio.enter_room(sid, room)
    print(f"{sid} joined room {room}")


# await sio.emit("event_name", {"data": "value"}, room="pongRoom")


@sio.event
async def leave(sid, data):
    room = data["room"]
    await sio.leave_room(sid, room)


@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")


@sio.event
async def ping(sid, data):
    await sio.emit("pong", {"message": "pong"}, to=sid)
