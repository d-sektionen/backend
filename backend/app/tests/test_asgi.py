import threading
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

from django.test import SimpleTestCase

from ..asgi import _run_periodic_command


class PeriodicCommandTests(SimpleTestCase):
    def test_closes_connections_after_successful_commands(self):
        for name, options in (("send_queued_mail", {"processes": 1}), ("nightly", {})):
            with self.subTest(command=name):
                with (
                    patch("django.core.management.call_command") as call_command,
                    patch("backend.app.asgi.connections.close_all") as close_all,
                ):
                    _run_periodic_command(name, **options)

                call_command.assert_called_once_with(name, **options)
                close_all.assert_called_once_with()

    def test_closes_connections_and_propagates_command_failure(self):
        error = RuntimeError("command failed")
        with (
            patch("django.core.management.call_command", side_effect=error),
            patch("backend.app.asgi.connections.close_all") as close_all,
        ):
            with self.assertRaises(RuntimeError) as raised:
                _run_periodic_command("nightly")

        self.assertIs(raised.exception, error)
        close_all.assert_called_once_with()

    def test_closes_connections_in_the_command_worker_thread(self):
        events = []

        def run_command(*args, **kwargs):
            events.append(("command", threading.get_ident()))

        def close_connections():
            events.append(("close", threading.get_ident()))

        with (
            patch("django.core.management.call_command", side_effect=run_command),
            patch(
                "backend.app.asgi.connections.close_all", side_effect=close_connections
            ),
        ):
            with ThreadPoolExecutor(max_workers=1) as executor:
                executor.submit(_run_periodic_command, "nightly").result(timeout=5)

        worker_thread = events[0][1]
        self.assertNotEqual(worker_thread, threading.get_ident())
        self.assertEqual(events, [("command", worker_thread), ("close", worker_thread)])
