from asgiref.sync import async_to_sync
from rest_framework.decorators import (
    action,
)
from rest_framework import viewsets
from rest_framework.response import Response
import datetime
from rest_framework import status
from django.conf import settings
from yalexs.exceptions import AugustApiAIOHTTPError
from account.permissions import AllowMembers
from .utils import YaleApi
from logger.utils import log, Entry


BETTAN_LOCK_ID = settings.BETTAN_LOCK_ID
CONFIGURA_LOCK_ID = settings.CONFIGURA_LOCK_ID


def handle_lock_command(command, lock_id, user):
    """
    Unlocks or locks the door with lock_id.
    """

    async def lock_command(command, lock_id):
        async with YaleApi() as api:
            yale_api = await api.get_api()
            yale_authenticate = await api.get_authentication()

            if command == "unlock":
                await yale_api.async_unlock(
                    access_token=yale_authenticate.access_token, lock_id=lock_id
                )
            elif command == "lock":
                await yale_api.async_lock(
                    access_token=yale_authenticate.access_token, lock_id=lock_id
                )

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
    if lock_id == BETTAN_LOCK_ID:
        log_entry_type = Entry.NETLIGHT
    elif lock_id == CONFIGURA_LOCK_ID:
        log_entry_type = Entry.CONFIGURA

    if not log(command, log_entry_type, user=user):
        return Response(
            {"detail": "Unable to log request."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    try:
        async_to_sync(lock_command, force_new_loop=True)(command, lock_id)

        # Respond to success
        msg = "upplåst" if command == "unlock" else "låst"
        return Response(
            {"detail": "Dörren är nu på väg att bli " + msg + "."},
            status=status.HTTP_200_OK,
        )
    except AugustApiAIOHTTPError:
        return Response(
            {
                "detail": "Problem i kommunikationen med låset. Kontakta webmaster!",
                "status": "500",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


async def get_lock_status(lock_id):
    async with YaleApi() as api:
        yale_api = await api.get_api()
        yale_authenticate = await api.get_authentication()

        try:
            lock = await yale_api.async_get_lock_detail(
                lock_id=lock_id, access_token=yale_authenticate.access_token
            )
        except AugustApiAIOHTTPError:
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


class ConfiguraViewSet(viewsets.ViewSet):
    permission_classes = (AllowMembers,)

    def list(self, request):
        return async_to_sync(get_lock_status)(lock_id=CONFIGURA_LOCK_ID)

    @action(detail=False, methods=["post"])
    def unlock(self, request):
        return handle_lock_command("unlock", CONFIGURA_LOCK_ID, request.user)

    @action(detail=False, methods=["post"])
    def lock(self, request):
        return handle_lock_command("lock", CONFIGURA_LOCK_ID, request.user)


class BettanViewSet(viewsets.ViewSet):
    permission_classes = (AllowMembers,)

    def list(self, request):
        return async_to_sync(get_lock_status)(lock_id=BETTAN_LOCK_ID)

    @action(detail=False, methods=["post"])
    def unlock(self, request):
        return handle_lock_command("unlock", BETTAN_LOCK_ID, request.user)

    @action(detail=False, methods=["post"])
    def lock(self, request):
        return handle_lock_command("lock", BETTAN_LOCK_ID, request.user)
