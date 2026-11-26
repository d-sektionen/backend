import asyncio
import threading
from unittest import skipUnless
from unittest.mock import patch

from asgiref.sync import markcoroutinefunction
from asgiref.testing import ApplicationCommunicator
from django.core import signals
from django.http import HttpResponse, StreamingHttpResponse
from django.db import connection, connections
from django.test import SimpleTestCase, TransactionTestCase, override_settings
from django.urls import path
from django.utils.deprecation import MiddlewareMixin

from backend.app.handlers import SyncMiddlewareASGIHandler


class ThreadTraceMiddleware(MiddlewareMixin):
    events = []

    def process_request(self, request):
        self.events.append(("request", threading.get_ident()))

    def process_response(self, request, response):
        self.events.append(("response", threading.get_ident()))
        return response


def sync_view(request):
    ThreadTraceMiddleware.events.append(("view", threading.get_ident()))
    return HttpResponse("anonymous=" + str(request.user.is_anonymous))


async def async_view(request):
    await asyncio.sleep(0)
    return HttpResponse("async")


def stream_view(request):
    return StreamingHttpResponse(iter([b"first", b"second"]))


def error_view(request):
    raise ValueError("test handler failure")


urlpatterns = [
    path("sync/", sync_view),
    path("async/", async_view),
    path("stream/", stream_view),
    path("error/", error_view),
]


@override_settings(ROOT_URLCONF=__name__, ALLOWED_HOSTS=["localhost"], DEBUG=False)
class SyncMiddlewareHandlerTests(SimpleTestCase):
    async def request(self, handler, path="/sync/", method="GET", extra_headers=()):
        app = ApplicationCommunicator(
            handler,
            {
                "type": "http",
                "asgi": {"version": "3.0"},
                "http_version": "1.1",
                "method": method,
                "path": path,
                "raw_path": path.encode(),
                "query_string": b"",
                "headers": [(b"host", b"localhost"), *extra_headers],
                "server": ("localhost", 80),
                "client": ("127.0.0.1", 12345),
                "scheme": "http",
            },
        )
        await app.send_input({"type": "http.request", "body": b""})
        messages = []
        while (
            not messages
            or messages[-1]["type"] != "http.response.body"
            or messages[-1].get("more_body", False)
        ):
            messages.append(await app.receive_output(timeout=3))
        await app.wait(timeout=3)
        return messages

    async def test_middleware_view_and_cleanup_share_request_thread(self):
        from django.conf import settings

        events = ThreadTraceMiddleware.events = []
        main_thread = threading.get_ident()

        def started(**kwargs):
            events.append(("started", threading.get_ident()))

        def finished(**kwargs):
            events.append(("finished", threading.get_ident()))

        signals.request_started.connect(started, weak=False)
        signals.request_finished.connect(finished, weak=False)
        try:
            with override_settings(
                MIDDLEWARE=[__name__ + ".ThreadTraceMiddleware", *settings.MIDDLEWARE]
            ):
                messages = await self.request(SyncMiddlewareASGIHandler())
        finally:
            signals.request_started.disconnect(started)
            signals.request_finished.disconnect(finished)
        self.assertEqual(messages[0]["status"], 200)
        self.assertEqual(messages[1]["body"], b"anonymous=True")
        self.assertEqual(
            [name for name, _ in events],
            ["started", "request", "view", "response", "finished"],
        )
        self.assertEqual(len({ident for _, ident in events}), 1)
        self.assertNotEqual(events[0][1], main_thread)
        self.assertIn((b"X-Frame-Options", b"DENY"), messages[0]["headers"])

    async def test_csrf_and_cors_middleware_remain_effective(self):
        with override_settings(CORS_ALLOWED_ORIGINS=["http://local-browser.test"]):
            handler = SyncMiddlewareASGIHandler()
            denied = await self.request(handler, method="POST")
            cors = await self.request(
                handler, extra_headers=[(b"origin", b"http://local-browser.test")]
            )
        self.assertEqual(denied[0]["status"], 403)
        self.assertIn(
            (b"access-control-allow-origin", b"http://local-browser.test"),
            cors[0]["headers"],
        )

    async def test_async_view_streaming_and_error_conversion(self):
        handler = SyncMiddlewareASGIHandler()
        response = await self.request(handler, path="/async/")
        self.assertEqual(response[0]["status"], 200)
        self.assertEqual(response[1]["body"], b"async")
        with self.assertWarnsRegex(Warning, "synchronous iterators"):
            streamed = await self.request(handler, path="/stream/")
        self.assertEqual(b"".join(m.get("body", b"") for m in streamed), b"firstsecond")
        with self.assertLogs("django.request", level="ERROR"):
            error = await self.request(handler, path="/error/")
        self.assertEqual(error[0]["status"], 500)

    async def test_concurrent_requests_do_not_block_event_loop_or_share_thread(self):
        entered = set()
        lock = threading.Lock()
        release = threading.Event()

        def held_view(request):
            with lock:
                entered.add(threading.get_ident())
            if not release.wait(3):
                raise TimeoutError("requests did not overlap")
            return HttpResponse("released")

        handler = SyncMiddlewareASGIHandler()
        with (
            patch(__name__ + ".sync_view", held_view),
            patch.object(urlpatterns[0], "callback", held_view),
        ):
            requests = [asyncio.create_task(self.request(handler)) for _ in range(2)]
            try:
                async with asyncio.timeout(2):
                    while len(entered) < 2:
                        await asyncio.sleep(0.001)
            finally:
                release.set()
            responses = await asyncio.gather(*requests)
        self.assertEqual(len(entered), 2)
        self.assertTrue(all(r[0]["status"] == 200 for r in responses))


class AsyncOnlyMiddleware:
    sync_capable = False
    async_capable = True

    def __init__(self, get_response):
        self.get_response = get_response
        markcoroutinefunction(self)

    async def __call__(self, request):
        await asyncio.sleep(0)
        response = await self.get_response(request)
        response["X-Async-Middleware"] = "ran"
        return response


@override_settings(ROOT_URLCONF=__name__, ALLOWED_HOSTS=["localhost"])
class AdditionalHandlerTests(SimpleTestCase):
    request = SyncMiddlewareHandlerTests.request

    async def test_async_only_middleware_can_wrap_sync_view(self):
        from django.conf import settings

        with override_settings(
            MIDDLEWARE=[__name__ + ".AsyncOnlyMiddleware", *settings.MIDDLEWARE]
        ):
            messages = await self.request(SyncMiddlewareASGIHandler())
        self.assertEqual(messages[0]["status"], 200)
        self.assertIn((b"X-Async-Middleware", b"ran"), messages[0]["headers"])

    async def test_disconnect_during_body_does_not_dispatch(self):
        with patch("django.core.handlers.asgi.signals.request_started.send") as started:
            app = ApplicationCommunicator(SyncMiddlewareASGIHandler(), {"type": "http"})
            await app.send_input({"type": "http.disconnect"})
            await app.wait(timeout=1)
            self.assertTrue(await app.receive_nothing())
        started.assert_not_called()


@override_settings(ROOT_URLCONF=__name__, ALLOWED_HOSTS=["localhost"])
@skipUnless(
    connection.vendor == "postgresql", "Requires request-scoped PostgreSQL connections"
)
class HandlerConnectionTests(TransactionTestCase):
    request = SyncMiddlewareHandlerTests.request

    async def test_real_database_connection_closes_at_request_end(self):
        opened = []

        def database_view(request):
            wrapper = connections["default"]
            with wrapper.cursor() as cursor:
                cursor.execute("SELECT 1")
                assert cursor.fetchone() == (1,)
            opened.append(wrapper)
            return HttpResponse("database")

        with patch.object(urlpatterns[0], "callback", database_view):
            messages = await self.request(SyncMiddlewareASGIHandler())
        self.assertEqual(messages[0]["status"], 200)
        self.assertEqual(len(opened), 1)
        self.assertIsNone(opened[0].connection)
