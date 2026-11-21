import socketio
from django.test import SimpleTestCase, override_settings

from backend.app import sockets


class CreateServerTests(SimpleTestCase):
    @override_settings(REDIS_URL=None)
    def test_no_redis_url_uses_in_memory_manager(self):
        server = sockets._create_server()
        self.assertIs(type(server.manager), socketio.AsyncManager)

    @override_settings(REDIS_URL="redis://localhost:6379")
    def test_redis_url_uses_redis_manager(self):
        # Constructing AsyncRedisManager does not connect, so no Redis is needed.
        server = sockets._create_server()
        self.assertIsInstance(server.manager, socketio.AsyncRedisManager)
