from datetime import datetime, timedelta
from typing import Generic, Optional, TypeVar
from dataclasses import dataclass

T = TypeVar("T")


@dataclass
class CachedValue(Generic[T]):
    value: T
    timestamp: datetime


class SingleValueTimedCache(Generic[T]):
    def __init__(self, expiration_duration: timedelta = timedelta(days=1)) -> None:
        self._entry: Optional[CachedValue[T]] = None
        self._expiration_duration = expiration_duration

    def _is_expired(self, entry: CachedValue[T]) -> bool:
        return datetime.now() - entry.timestamp > self._expiration_duration

    def get(self) -> Optional[T]:
        if self._entry is None:
            return None

        if self._is_expired(self._entry):
            self._entry = None
            return None

        return self._entry.value

    def set(self, value: T) -> None:
        self._entry = CachedValue(value=value, timestamp=datetime.now())

    def clear(self) -> None:
        self._entry = None
