import datetime

from django.contrib.auth.models import User
from app.settings_shared import HOME_ASSISTANT_BASEURL, HOME_ASSISTANT_TOKEN
from logger.utils import log
from rest_framework import status
import requests

from .utils import (
    LOCK_INTERNAL_ERROR_RESPONSE,
    LOCK_LOG_ENTRY_TYPE,
    LockCommand,
    LockID,
    LockStatus,
    lock_command_response,
)


def lock_command(command: LockCommand, lock_id: LockID, user: User):
    """Unlocks or locks the door with lock_id."""
    try:
        lock = _get_lock_status(lock_id)
    except requests.RequestException:
        return LOCK_INTERNAL_ERROR_RESPONSE

    # Limit time of day when people can unlock door, they should still be able to lock at any time.
    now = datetime.datetime.now()
    todayMorningLimit = now.replace(hour=5, minute=0, second=0, microsecond=0)
    todayEveningLimit = now.replace(hour=21, minute=0, second=0, microsecond=0)
    notWithinLimits = todayEveningLimit < now < todayMorningLimit

    if command == LockCommand.UNLOCK and notWithinLimits:
        return lock_command_response(
            lock,
            f"Det går endast att låsa upp mellan {todayMorningLimit.strftime('%H:%M')} och {todayEveningLimit.strftime('%H:%M')}.",
            status.HTTP_400_BAD_REQUEST,
        )

    if lock.get("lock_status") == LockStatus.LOCKED and command == LockCommand.LOCK:
        return lock_command_response(
            lock,
            "Låset är redan låst!",
            status.HTTP_200_OK,
        )

    if lock.get("lock_status") == LockStatus.UNLOCKED and command == LockCommand.UNLOCK:
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

    headers = {"Authorization": f"Bearer {HOME_ASSISTANT_TOKEN}"}
    data = {"entity_id": lock_id.value}
    requests.post(
        f"{HOME_ASSISTANT_BASEURL}/services/lock/{command.value}",
        headers=headers,
        json=data,
    )

    # Respond to success
    locking_action = "upplåst" if command == LockCommand.UNLOCK else "låst"
    return lock_command_response(
        lock, f"Dörren är nu på väg att bli {locking_action}!", status.HTTP_200_OK
    )


def get_lock_status(lock_id: LockID):
    """
    Responds with lock status data for lock with lock_id'
    """
    try:
        lock_status = _get_lock_status(lock_id)
    except requests.RequestException:
        return LOCK_INTERNAL_ERROR_RESPONSE

    # When all is good, return lock data with no message
    return lock_command_response(lock_status, "", status=status.HTTP_200_OK)


def _get_lock_status(lock_id: LockID):
    headers = {"Authorization": f"Bearer {HOME_ASSISTANT_TOKEN}"}
    lock = requests.get(
        f"{HOME_ASSISTANT_BASEURL}/states/{lock_id.value}", headers=headers
    )

    lock_json = lock.json()

    if lock_json["state"] == "unavailable":
        return {"battery_level": 0, "bridge_is_online": False, "is_unlocked": False}

    return {
        "battery_level": lock_json["attributes"]["battery_level"],
        "bridge_is_online": True,
        "is_unlocked": True if lock_json["state"] == "unlocked" else False,
    }
