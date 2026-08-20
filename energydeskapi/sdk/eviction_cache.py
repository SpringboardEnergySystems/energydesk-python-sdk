from datetime import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CacheEntry[T]:
    value: T
    last_accessed: datetime  # Timestamp of the last access


class EvictionCache[K, T]:
    # keeps a cache of max max_size entries and removes the oldest accessed entries when new entries are added beyond the max size
    def __init__(self, max_size: int):
        self.cache: dict[K, CacheEntry[T]] = {}
        self._max_size = max_size


    def put(self, key: K, value: T) -> None:
        self.cache[key] = CacheEntry(value=value, last_accessed=datetime.now())
        self._evict_old_entries()

    def get(self, key: K) -> Optional[T]:
        found = self.cache.get(key)
        if found is not None:
            self.cache[key] = CacheEntry(value=found.value, last_accessed=datetime.now())  # Update last accessed time
            return found.value
        else:
            return None

    @staticmethod
    def _get_last_accessed_time(item: tuple[K, CacheEntry[T]]) -> datetime:
        key, entry = item
        return entry.last_accessed

    def _evict_old_entries(self) -> None:
        if  len(self.cache) > self._max_size:
            # Sort entries by last accessed time and evict the oldest
            sorted_entries = sorted(self.cache.items(), key=EvictionCache._get_last_accessed_time)
            for i in range(len(self.cache) - self._max_size):
                key, entry = sorted_entries[i]
                del self.cache[key]
