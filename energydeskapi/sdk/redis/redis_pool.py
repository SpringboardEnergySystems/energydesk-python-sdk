import os
import time
import uuid
import logging
from contextlib import contextmanager
from redis.client import StrictRedis

logger = logging.getLogger(__name__)
_redis: StrictRedis | None = None

def _get_redis() -> StrictRedis:
    """Lazily create and cache a StrictRedis connection."""
    global _redis
    if _redis is None:
        host = os.getenv("REDIS_HOST", "localhost")
        port = int(os.getenv("REDIS_PORT", 6379))
        db = int(os.getenv("REDIS_DB", 1))
        timeout = int(os.getenv("REDIS_TIMEOUT_SECONDS", 1))
        pwd = os.getenv("REDIS_PASSWORD", None)

        logger.info(f"Connecting to Redis {host}:{port} db={db}")
        _redis = StrictRedis(
            host=host,
            port=port,
            db=db,
            password=pwd,
            socket_timeout=timeout,
            socket_connect_timeout=timeout,
            decode_responses=False,
        )
        _redis.ping()
        logger.info("Connected to Redis")
    return _redis

class RedisPool:
    """
    Counting pool stored in Redis.

    Each holder writes a member with score = expiry_ts and value = uuid token.
    Crashed holders disappear automatically after ttl seconds.
    """

    def __init__(self, name: str, limit: int, ttl: int = 60 * 30):
        self.key = f"sync:{name}"
        self.limit = limit
        self.ttl = ttl
        self.r = _get_redis()

    def _clean(self) -> None:
        """Remove expired holders."""
        now = time.time()
        # ZREMRANGEBYSCORE key -inf now
        self.r.zremrangebyscore(self.key, 0, now)

    @contextmanager # to use 'with'
    def acquire(self, block: bool = True, poll: float = 1.0):
        """
        Grab a slot (`block` or raise RuntimeError) and yield.
        Always frees the slot in finally block.
        """
        token = uuid.uuid4().hex
        expiry = time.time() + self.ttl

        while True:
            pipe = self.r.pipeline()
            self._clean()
            pipe.zcard(self.key)
            pipe.zadd(self.key, {token: expiry}, nx=True)
            card, added = pipe.execute()

            if card < self.limit and added == 1:
                try:
                    yield
                finally:
                    self.r.zrem(self.key, token)
                return

            if not block:
                raise RuntimeError("Pool limit reached")

            time.sleep(poll)


