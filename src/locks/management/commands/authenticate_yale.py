import os
import aiohttp
from django.core.management.base import BaseCommand
from yalexs.api_async import ApiAsync
from yalexs.authenticator_async import AuthenticationState, AuthenticatorAsync
from yalexs.const import Brand
from asgiref.sync import async_to_sync

YALE_EMAIL = os.getenv("YALE_EMAIL")
YALE_PASSWORD = os.getenv("YALE_PASSWORD")


class Command(BaseCommand):
    help = "Authenticate to Yale API and create a cached token file."

    async def yale_auth(self):
        session = aiohttp.ClientSession()
        yale_api = ApiAsync(aiohttp_session=session, timeout=20, brand=Brand.YALE_HOME)
        yale_authenticator = AuthenticatorAsync(
            yale_api,
            "email",
            YALE_EMAIL,
            YALE_PASSWORD,
            access_token_cache_file=".YALE_ACCESS_TOKEN_CACHE",
        )

        await yale_authenticator.async_setup_authentication()
        await yale_authenticator.async_authenticate()

        yale_authenticate = await yale_authenticator.async_authenticate()

        if yale_authenticate.state == AuthenticationState.BAD_PASSWORD:
            await session.close()
            return self.stdout.write("Email or password is invalid")

        if yale_authenticate.state == AuthenticationState.REQUIRES_VALIDATION:
            await yale_authenticator.async_send_verification_code()
            verification_code = input(
                "Please provide the verification code that was sent to your email: "
            )
            await yale_authenticator.async_validate_verification_code(verification_code)
            await yale_authenticator.async_authenticate()

        if yale_authenticate.state == AuthenticationState.AUTHENTICATED:
            await session.close()
            return self.stdout.write(
                f"Authenticated successfully! The token expires {yale_authenticate.access_token_expires}"
            )

        self.stdout.write(
            f"Something went wrong when authenticating! Status: {yale_authenticate.state}"
        )
        await session.close()

    def handle(self, *args, **options):
        async_to_sync(self.yale_auth)()
