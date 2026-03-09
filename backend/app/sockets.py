# backend/app/sockets.py
import socketio

sio = socketio.AsyncServer(
    async_mode="asgi", cors_allowed_origins=["http://localhost:4000"]
)


@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")


@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")


@sio.event
async def join(sid, data):
    await sio.enter_room(sid, data["room"])


@sio.event
async def ping(sid, data):
    await sio.emit("pong", {"message": "pong"}, to=sid)
