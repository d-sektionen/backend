"""Adapt the synchronous HTTP stack once, keeping native ASGI I/O.

Django 4.2's async-capable middleware bridges each synchronous hook separately.
Our HTTP views are synchronous, so load the ordinary synchronous middleware/view
chain and adapt that chain once. ASGIHandler still owns request thread contexts,
body/response streaming, lifecycle signals and connection cleanup. Async-only
middleware and async views keep Django's normal sync/async adaptations.
"""

from asgiref.sync import sync_to_async
from django.core.handlers.asgi import ASGIHandler


class SyncMiddlewareASGIHandler(ASGIHandler):
    def load_middleware(self, is_async=False):
        super().load_middleware(is_async=False)
        if is_async:
            self._middleware_chain = sync_to_async(
                self._middleware_chain, thread_sensitive=True
            )
