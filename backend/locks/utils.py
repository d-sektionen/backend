from enum import Enum

from django.conf import settings
from ..logger.models import Entry
from rest_framework import status
from rest_framework.response import Response


class LockID(Enum):
    BETTAN = settings.BETTAN_LOCK_ID
    CONFIGURA = settings.CONFIGURA_LOCK_ID


class LockCommand(Enum):
    LOCK = "lock"
    UNLOCK = "unlock"


class LockStatus(Enum):
    # Replace with yalexs LockStatus if we ever use that again
    LOCKED = "locked"
    UNLOCKED = "unlocked"


LOCK_LOG_ENTRY_TYPE = {
    LockID.BETTAN: Entry.NETLIGHT,
    LockID.CONFIGURA: Entry.CONFIGURA,
}


def lock_command_response(lock, message: str, status: int):
    return Response(
        {
            "message": message,
            "battery_percentage": lock.get("battery_level"),
            "online": lock.get("bridge_is_online"),
            "unlocked": lock.get("is_unlocked"),
        },
        status=status,
    )


def lock_not_online_response(lock):
    return Response(
        {
            "message": "Låset är inte online. Kontakta webmaster vid frågor.",
            "battery_percentage": lock.get("battery_level"),
            "online": lock.get("bridge_is_online"),
            "unlocked": lock.get("is_unlocked"),
        },
        status=status,
    )


LOCK_INTERNAL_ERROR_RESPONSE = Response(
    {
        "message": "Problem i kommunikationen med låset. Kontakta webmaster!",
        "battery_percentage": 0,
        "online": False,
        "unlocked": False,
    },
    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
)
