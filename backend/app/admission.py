"""Bound database-using HTTP requests before Django allocates worker threads."""

import asyncio


class HTTPConcurrencyMiddleware:
    def __init__(self, application, limit):
        if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
            raise ValueError("ASGI_HTTP_CONCURRENCY must be a positive integer")
        self.application = application
        self.slots = asyncio.Semaphore(limit)

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.application(scope, receive, send)
        async with self.slots:
            return await self.application(scope, receive, send)
