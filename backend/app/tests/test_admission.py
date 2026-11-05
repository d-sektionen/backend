import asyncio
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock

from backend.app.admission import HTTPConcurrencyMiddleware


class HTTPConcurrencyTests(IsolatedAsyncioTestCase):
    async def test_queues_before_entering_application_and_bypasses_non_http(self):
        release = asyncio.Event()
        full = asyncio.Event()
        active = 0
        peak = 0
        entered = []

        async def application(scope, receive, send):
            nonlocal active, peak
            if scope["type"] != "http":
                return "socket"
            active += 1
            peak = max(peak, active)
            entered.append(scope["id"])
            if active == 2:
                full.set()
            await release.wait()
            active -= 1

        limited = HTTPConcurrencyMiddleware(application, 2)
        tasks = [
            asyncio.create_task(limited({"type": "http", "id": i}, None, None))
            for i in range(6)
        ]
        await asyncio.wait_for(full.wait(), 1)
        self.assertEqual(len(entered), 2)
        self.assertEqual(
            await asyncio.wait_for(limited({"type": "websocket"}, None, None), 1),
            "socket",
        )
        release.set()
        await asyncio.wait_for(asyncio.gather(*tasks), 1)
        self.assertEqual(peak, 2)
        self.assertEqual(entered, list(range(6)))

    async def test_failure_and_cancelled_requests_release_slots(self):
        entered = asyncio.Event()

        async def application(scope, receive, send):
            entered.set()
            await asyncio.Future()

        limited = HTTPConcurrencyMiddleware(application, 1)
        running = asyncio.create_task(limited({"type": "http"}, None, None))
        await asyncio.wait_for(entered.wait(), 1)
        waiting = asyncio.create_task(limited({"type": "http"}, None, None))
        await asyncio.sleep(0)
        waiting.cancel()
        running.cancel()
        for task in (waiting, running):
            with self.assertRaises(asyncio.CancelledError):
                await task
        limited.application = AsyncMock(side_effect=RuntimeError("application failed"))
        with self.assertRaisesRegex(RuntimeError, "application failed"):
            await asyncio.wait_for(limited({"type": "http"}, None, None), 1)
        limited.application = AsyncMock(return_value="ok")
        self.assertEqual(
            await asyncio.wait_for(limited({"type": "http"}, None, None), 1), "ok"
        )

    def test_invalid_limits_fail_at_startup(self):
        for limit in (0, -1, True, 1.5, "8"):
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                HTTPConcurrencyMiddleware(None, limit)
