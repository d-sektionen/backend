import os
import aiohttp
from yalexs.api_async import ApiAsync
from yalexs.authenticator_async import AuthenticatorAsync
from yalexs.const import Brand


class YaleApi:
    """Context manager for yalexs."""

    _session = None
    _yale_api = None
    _yale_authenticator = None
    _yale_authentication = None

    def __init__(self):
        self._session = aiohttp.ClientSession()

    async def get_session(self):
        if not self._session:
            self._session = aiohttp.ClientSession()
        return self._session

    async def get_authentication(self):
        if self._yale_authentication is None:
            authenticator = await self.get_authenticator()
            await authenticator.async_setup_authentication()
            self._yale_authentication = await authenticator.async_authenticate()

        return self._yale_authentication

    async def get_authenticator(self):
        """Constructs an AuthenticatorAsync instance."""
        if self._yale_authenticator is None:
            YALE_EMAIL = os.getenv("YALE_EMAIL")
            YALE_PASSWORD = os.getenv("YALE_PASSWORD")

            api = await self.get_api()
            self._yale_authenticator = AuthenticatorAsync(
                api,
                "email",
                YALE_EMAIL,
                YALE_PASSWORD,
                access_token_cache_file=".YALE_ACCESS_TOKEN_CACHE",
            )

        return self._yale_authenticator

    async def get_api(self):
        """Constructs an ApiAsync instance."""
        if self._yale_api is None:
            self._yale_api = ApiAsync(
                aiohttp_session=await self.get_session(),
                timeout=20,
                brand=Brand.YALE_HOME,
            )

        return self._yale_api

    async def __aenter__(self):
        return self

    async def __aexit__(self, *excinfo):
        await self._session.close()
