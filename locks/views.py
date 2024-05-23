from rest_framework.decorators import (
    action,
)
from rest_framework import viewsets
from rest_framework.response import Response
import datetime
from rest_framework import status
from django.conf import settings
from yalexs.const import Brand
from yalexs.exceptions import AugustApiHTTPError
from yalexs.api import Api
from yalexs.authenticator import Authenticator, AuthenticationState
from account.permissions import AllowMembers
from logger.utils import log, Entry


BETTAN_LOCK_ID = settings.BETTAN_LOCK_ID
YALE_EMAIL = settings.YALE_EMAIL
YALE_PASSWORD = settings.YALE_PASSWORD

yale_api = Api(timeout=20, brand=Brand.YALE_HOME)
yale_authenticator = Authenticator(
    yale_api,
    "email",
    YALE_EMAIL,
    YALE_PASSWORD,
    access_token_cache_file=".YALE_ACCESS_TOKEN_CACHE",
)
yale_authenticate = yale_authenticator.authenticate()


class BettanViewSet(viewsets.ViewSet):
    permission_classes = (AllowMembers,)

    def list(self, request):
        try:
            lock = yale_api.get_lock_detail(
                lock_id=BETTAN_LOCK_ID, access_token=yale_authenticate.access_token
            )
        except AugustApiHTTPError as e:
            print(e)
            return Response(
                {
                    "detail": "Problem i kommunikationen med låset. Kontakta webmaster!",
                    "status": "500",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "status": lock.bridge_is_online,  # Not 1:1 with previous implementation
                "battery_percentage": lock.battery_level,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"])
    def unlock(self, request):
        return self.lock_command("unlock", request.user)

    @action(detail=False, methods=["post"])
    def lock(self, request):
        return self.lock_command("lock", request.user)

    def lock_command(self, command, user):
        """
        Unlocks or locks the Bettan door.
        """
        now = datetime.datetime.now()

        # Limit time of day when people can unlock door, they should still be able to lock at any time.
        todayMorningLimit = now.replace(hour=5, minute=0, second=0, microsecond=0)
        todayEveningLimit = now.replace(hour=21, minute=0, second=0, microsecond=0)
        notWithinLimits = now > todayEveningLimit or now < todayMorningLimit

        if command == "unlock" and notWithinLimits:
            return Response(
                {
                    "detail": "Det går endast att låsa upp mellan "
                    + todayMorningLimit.strftime("%H:%M")
                    + " och "
                    + todayEveningLimit.strftime("%H:%M")
                    + "."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Log action and send request
        if not log(command, Entry.NETLIGHT, user=user):
            return Response(
                {"detail": "Unable to log request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:
            if command == "unlock":
                yale_api.unlock(
                    access_token=yale_authenticate.access_token, lock_id=BETTAN_LOCK_ID
                )
            elif command == "lock":
                yale_api.lock(
                    access_token=yale_authenticate.access_token, lock_id=BETTAN_LOCK_ID
                )
            else:
                return Response({"detail": "Invalid command."}, status=status.HTTP_400_BAD_REQUEST)

            # Respond to success
            msg = "upplåst" if command == "unlock" else "låst"
            return Response(
                {"detail": "Dörren är nu på väg att bli " + msg + "."},
                status=status.HTTP_200_OK,
            )
        except AugustApiHTTPError as e:
            print(e)
            return Response(
                {
                    "detail": "Problem i kommunikationen med låset. Kontakta webmaster!",
                    "status": "500",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
