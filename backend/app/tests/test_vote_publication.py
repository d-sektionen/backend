import asyncio
import time
from unittest.mock import patch

from django.test import SimpleTestCase

from backend.app.sockets import emit_event
from backend.voting.signals import _publish_event


class VotePublicationTests(SimpleTestCase):
    def test_slow_publication_has_a_deadline_after_commit(self):
        cancelled = []

        async def slow_emit(*args, **kwargs):
            try:
                await asyncio.sleep(2)
            except asyncio.CancelledError:
                cancelled.append(True)
                raise

        with (
            patch("backend.voting.signals.emit_event", emit_event),
            patch("backend.app.sockets.sio.emit", side_effect=slow_emit),
            self.assertLogs("backend.voting.signals", level="WARNING"),
        ):
            started = time.monotonic()
            _publish_event("update_alternative", {"id": 0}, "local-test")
            elapsed = time.monotonic() - started
        self.assertLess(elapsed, 1.5)
        self.assertEqual(cancelled, [True])
