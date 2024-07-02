import os
from django.core.management.base import BaseCommand
from yalexs.api import Api
from yalexs.authenticator import AuthenticationState, Authenticator
from yalexs.const import Brand

YALE_EMAIL = os.getenv("YALE_EMAIL")
YALE_PASSWORD = os.getenv("YALE_PASSWORD")

class Command(BaseCommand):
    help = "Authenticate to Yale API and create a cached token file."

    def handle(self, *args, **kwargs):
        yale_api = Api(timeout=20, brand=Brand.YALE_HOME)
        yale_authenticator = Authenticator(
            yale_api,
            "email",
            YALE_EMAIL,
            YALE_PASSWORD,
            access_token_cache_file=".YALE_ACCESS_TOKEN_CACHE",
        )

        yale_authenticate = yale_authenticator.authenticate()

        print(yale_authenticate.state)

        if yale_authenticate.state == AuthenticationState.BAD_PASSWORD:
            return self.stdout.write(f"Email or password is invalid")

        if yale_authenticate.state == AuthenticationState.REQUIRES_VALIDATION:
            yale_authenticator.send_verification_code()
            verification_code = input(
                "Please provide the verification code that was sent to your email: "
            )
            yale_authenticator.validate_verification_code(verification_code)
            yale_authenticate = yale_authenticator.authenticate()

        if yale_authenticate.state == AuthenticationState.AUTHENTICATED:
            return self.stdout.write(f"Authenticated successfully! The token expires {yale_authenticate.access_token_expires}")
        
        self.stdout.write(f"Something went wrong when authenticating! Status: {yale_authenticate.state}")
