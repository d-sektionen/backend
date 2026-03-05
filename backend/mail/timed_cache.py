from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass


@dataclass
class CachedValue[T]:
    value: T
    timestamp: datetime


class SingleValueTimedCache[T]:
    def __init__(self, expiration_duration: timedelta = timedelta(days=1)) -> None:
        self._entry: Optional[CachedValue[T]] = None
        self._expiration_duration = expiration_duration

    def _is_expired(self, entry: CachedValue[T]) -> bool:
        """Check if the cached entry is expired based on its timestamp."""
        return datetime.now() - entry.timestamp > self._expiration_duration

    def get(self) -> Optional[T]:
        """Retrieve the cached value if it exists and is not expired; otherwise, return None."""
        if self._entry is None:
            return None

        if self._is_expired(self._entry):
            self._entry = None
            return None

        return self._entry.value

    def set(self, value: T) -> None:
        """Set a new value in the cache with the current timestamp."""
        self._entry = CachedValue(value=value, timestamp=datetime.now())

    def clear(self) -> None:
        """Clear the cached value."""
        self._entry = None
