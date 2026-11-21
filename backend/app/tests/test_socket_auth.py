import threading
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from django.test import SimpleTestCase

from backend.app.sockets import connect


class SocketAuthenticationTests(SimpleTestCase):
    async def test_authentication_connection_closes_in_its_worker_thread(self):
        caller = threading.get_ident()
        events = []
        user = SimpleNamespace(id=1, username="local")

        def authenticate(request):
            events.append(("authenticate", threading.get_ident()))
            return user, object()

        def close():
            events.append(("close", threading.get_ident()))

        with (
            patch(
                "backend.oauth2.auth.CookieJWTAuthentication.authenticate",
                side_effect=authenticate,
            ),
            patch("django.db.connections.close_all", close),
            patch("backend.app.sockets.sio.save_session", new_callable=AsyncMock),
        ):
            await connect("local-test", {"HTTP_COOKIE": "access_token=local"})
        self.assertEqual([event for event, _ in events], ["authenticate", "close"])
        self.assertEqual(events[0][1], events[1][1])
        self.assertNotEqual(events[0][1], caller)

    async def test_authentication_failure_also_closes_connection(self):
        with (
            patch(
                "backend.oauth2.auth.CookieJWTAuthentication.authenticate",
                side_effect=RuntimeError("failure"),
            ),
            patch("django.db.connections.close_all") as close,
        ):
            with self.assertRaisesRegex(RuntimeError, "failure"):
                await connect("local-test", {"HTTP_COOKIE": "access_token=local"})
        close.assert_called_once_with()
