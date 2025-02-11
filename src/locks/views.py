import datetime

from account.permissions import AllowMembers
from asgiref.sync import async_to_sync
from rest_framework import throttling, viewsets
from rest_framework.decorators import action

from .lock import get_lock_status, handle_lock_command
from .utils import LockCommand, LockID


class LockGlobalThrottle(throttling.BaseThrottle):
    last_request_time = datetime.datetime.now()

    def allow_request(self, request, view):
        current_time = datetime.datetime.now()
        seconds_between_requests = 6

        if (
            current_time - self.last_request_time
        ).total_seconds() <= seconds_between_requests:
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
