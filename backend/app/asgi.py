# backend/app/asgi.py
from django.core.asgi import get_asgi_application
import socketio
from .sockets import sio

django_asgi_app = get_asgi_application()
application = socketio.ASGIApp(sio, django_asgi_app, socketio_path="/ws")
