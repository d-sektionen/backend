import datetime

from asgiref.sync import async_to_sync
from django.contrib.auth.models import User
from logger.utils import log
from rest_framework import status
from yalexs.exceptions import AugustApiAIOHTTPError
from yalexs.lock import LockStatus

from .utils import (
    LOCK_INTERNAL_ERROR_RESPONSE,
    LOCK_LOG_ENTRY_TYPE,
    LockCommand,
    LockID,
    lock_command_response,
    lock_not_online_response,
)
from .yaleapi import YaleApi


def handle_lock_command(command: LockCommand, lock_id: LockID, user: User):
    """
    Handles lock commands in a synchronous context
    """
    try:
        return async_to_sync(lock_command)(command, lock_id, user)
    except AugustApiAIOHTTPError:
        return LOCK_INTERNAL_ERROR_RESPONSE


async def lock_command(command: LockCommand, lock_id: LockID, user: User):
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


async def _lock_command(
    yale_api, yale_authenticate, command: LockCommand, lock_id: LockID, user: User
):
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


async def get_lock_status(lock_id: LockID):
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
