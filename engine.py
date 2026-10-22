import hashlib
import threading
import time
from typing import Any, Optional


class KeyValueEngine:

    def __init__(self, num_shards: int = 16):
        self.num_shards = num_shards
        # Each shard has its own dictionary and its own lock
        self.shards = [{} for _ in range(num_shards)]
        self.locks = [threading.Lock() for _ in range(num_shards)]

    def _get_shard_index(self, key: str) -> int:
        """Hash the key to consistently map it to one of the N shards."""
        hash_digest = hashlib.md5(key.encode("utf-8")).hexdigest()
        return int(hash_digest, 16) % self.num_shards

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Store a key-value pair with an optional Time-To-Live (TTL)."""
        idx = self._get_shard_index(key)
        expire_at = time.time() + ttl_seconds if ttl_seconds else None

        # Lock ONLY the specific shard needed for this key
        with self.locks[idx]:
            self.shards[idx][key] = {"value": value, "expire_at": expire_at}

    def get(self, key: str) -> Optional[Any]:
        """Retrieve a value if it exists and has not expired."""
        idx = self._get_shard_index(key)

        with self.locks[idx]:
            item = self.shards[idx].get(key)
            if not item:
                return None

            # Lazy expiration check
            if item["expire_at"] and time.time() > item["expire_at"]:
                del self.shards[idx][key]
                return None

            return item["value"]

    def delete(self, key: str) -> bool:
        """Remove a key from the store."""
        idx = self._get_shard_index(key)
        with self.locks[idx]:
            if key in self.shards[idx]:
                del self.shards[idx][key]
                return True
            return False