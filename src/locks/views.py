import datetime
from enum import Enum

from account.permissions import AllowMembers
from asgiref.sync import async_to_sync
from django.conf import settings
from logger.utils import Entry, log
from rest_framework import status, throttling, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from yalexs.exceptions import AugustApiAIOHTTPError
from yalexs.lock import LockStatus

from .utils import YaleApi


class LockID(Enum):
    BETTAN = settings.BETTAN_LOCK_ID
    CONFIGURA = settings.CONFIGURA_LOCK_ID


class LockCommand(Enum):
    LOCK = "lock"
    UNLOCK = "unlock"


LOCK_LOG_ENTRY_TYPE = {
    LockID.BETTAN: Entry.NETLIGHT,
    LockID.CONFIGURA: Entry.CONFIGURA,
}


def lock_command_response(lock, message: str, status: int):
    return Response(
        {
            "message": message,
            "battery_percentage": lock.battery_percentage,
            "online": lock.bridge_is_online,
        },
        status=status,
    )


def lock_not_online_response(lock):
    return Response(
        {
            "message": "Låset är inte online. Kontakta webmaster vid frågor.",
            "battery_percentage": lock.battery_percentage,
            "online": lock.bridge_is_online,
        },
        status=status,
    )


LOCK_INTERNAL_ERROR_RESPONSE = Response(
    {
        "message": "Problem i kommunikationen med låset. Kontakta webmaster!",
        "battery_percentage": 0,
        "online": False,
    },
    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
)


class LockGlobalThrottle(throttling.BaseThrottle):
    last_request_time = datetime.datetime.now()

    def allow_request(self, request, view):
        current_time = datetime.datetime.now()
        seconds_between_requests = 6

        if (current_time - self.last_request_time) <= seconds_between_requests:
            return False

        self.last_request_time = current_time
        return True


class BaseLockViewSet(viewsets.ViewSet):
    permission_classes = (AllowMembers,)
    throttle_classes = (LockGlobalThrottle,)
    lock_id = None

    def list(self, request):
        return async_to_sync(get_lock_status)(lock_id=self.lock_id)

    @action(detail=False, methods=["post"])
    def unlock(self, request):
        return handle_lock_command(LockCommand.UNLOCK, self.lock_id, request.user)

    @action(detail=False, methods=["post"])
    def lock(self, request):
        return handle_lock_command(LockCommand.LOCK, self.lock_id, request.user)


class ConfiguraViewSet(BaseLockViewSet):
    lock_id = LockID.CONFIGURA


class BettanViewSet(BaseLockViewSet):
    lock_id = LockID.BETTAN


def handle_lock_command(command, lock_id, user):
    """
    Handles lock commands in a synchronous context
    """
    try:
        return async_to_sync(lock_command)(command, lock_id, user)
    except AugustApiAIOHTTPError:
        return LOCK_INTERNAL_ERROR_RESPONSE


async def lock_command(command, lock_id, user):
    """
    Performs a lock command through yale api
    """
    response = LOCK_INTERNAL_ERROR_RESPONSE

    async with YaleApi() as api:
        yale_api = await api.get_api()
        yale_authenticate = await api.get_authentication()

        response = await _lock_command(
            yale_api, yale_authenticate, command, lock_id, user
        )

    return response


async def _lock_command(yale_api, yale_authenticate, command, lock_id, user):
    """
    Unlocks or locks the door with lock_id.
    """
    lock = await yale_api.async_get_lock_detail(
        lock_id=lock_id, access_token=yale_authenticate.access_token
    )

    now = datetime.datetime.now()

    # Limit time of day when people can unlock door, they should still be able to lock at any time.
    todayMorningLimit = now.replace(hour=5, minute=0, second=0, microsecond=0)
    todayEveningLimit = now.replace(hour=21, minute=0, second=0, microsecond=0)
    notWithinLimits = now > todayEveningLimit or now < todayMorningLimit

    if command == LockCommand.UNLOCK and notWithinLimits:
        return lock_command_response(
            lock,
            f"Det går endast att låsa upp mellan {todayMorningLimit.strftime('%H:%M')} och {todayEveningLimit.strftime('%H:%M')}.",
            status.HTTP_400_BAD_REQUEST,
        )

    if not lock.bridge_is_online:
        return lock_not_online_response(lock)

    if lock.lock_status == LockStatus.LOCKED and command == LockCommand.LOCK:
        return lock_command_response(
            lock,
            "Låset är redan låst!",
            status.HTTP_200_OK,
        )

    if lock.lock_status == LockStatus.UNLOCKED and command == LockCommand.UNLOCK:
        return lock_command_response(
            lock,
            "Låset är redan upplåst!",
            status.HTTP_200_OK,
        )

    # Log action and send request
    log_entry_type = LOCK_LOG_ENTRY_TYPE.get(lock_id, None)
    if not log(command, log_entry_type, user=user):
        return lock_command_response(
            lock,
            "Kunde inte logga förfrågan, avbryter.",
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    match command:
        case LockCommand.UNLOCK:
            await yale_api.async_unlock(
                access_token=yale_authenticate.access_token, lock_id=lock_id
            )
        case LockCommand.LOCK:
            await yale_api.async_lock(
                access_token=yale_authenticate.access_token, lock_id=lock_id
            )

    # Respond to success
    locking_action = "upplåst" if command == LockCommand.UNLOCK else "låst"
    return lock_command_response(
        lock, f"Dörren är nu på väg att bli {locking_action}!", status.HTTP_200_OK
    )


async def get_lock_status(lock_id):
    """
    Responds with lock status data for lock with lock_id'
    """
    async with YaleApi() as api:
        yale_api = await api.get_api()
        yale_authenticate = await api.get_authentication()

        try:
            lock = await yale_api.async_get_lock_detail(
                lock_id=lock_id, access_token=yale_authenticate.access_token
            )
            # If lock is offline return error message.
            if not lock.bridge_is_online:
                return lock_not_online_response(lock)

            # When all is good, return lock data with no message
            return lock_command_response(
                lock,
                "",
                status=status.HTTP_200_OK,
            )
        except AugustApiAIOHTTPError:
            return LOCK_INTERNAL_ERROR_RESPONSE
