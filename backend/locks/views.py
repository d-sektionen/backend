from ..account.permissions import AllowMembers
from rest_framework import throttling, viewsets
from rest_framework.decorators import action

from .lock import get_lock_status, lock_command
from .utils import LockCommand, LockID


class LockRateLimit(throttling.UserRateThrottle):
    def __init__(self):
        self.rate = 0  # Required to be set for some reason despite not being used.
        # 1 request per 3 seconds
        self.num_requests = 1
        self.duration = 6


class BaseLockViewSet(viewsets.ViewSet):
    permission_classes = (AllowMembers,)
    lock_id = None

    def list(self, request):
        return get_lock_status(lock_id=self.lock_id)

    @action(detail=False, methods=["post"], throttle_classes=[LockRateLimit])
    def unlock(self, request):
        return lock_command(LockCommand.UNLOCK, self.lock_id, request.user)

    @action(detail=False, methods=["post"], throttle_classes=[LockRateLimit])
    def lock(self, request):
        return lock_command(LockCommand.LOCK, self.lock_id, request.user)


class ConfiguraViewSet(BaseLockViewSet):
    lock_id = LockID.CONFIGURA


class BettanViewSet(BaseLockViewSet):
    lock_id = LockID.BETTAN
