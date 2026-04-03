from __future__ import annotations

import datetime as _dt
import json
import logging
from typing import Any

from nats.aio.client import Client as NATS
from nats.js.api import KeyValueConfig, RetentionPolicy, StorageType, StreamConfig
from nats.js.errors import NotFoundError

logger = logging.getLogger(__name__)


class NatsBus:
    def __init__(self, url: str):
        self.url = url
        self.nc = NATS()
        self.js = None
        # Tracks every stream we have ensured so they can be re-created
        # automatically after a NATS reconnect (e.g. pod restart).
        self._known_streams: dict[str, tuple[list[str], str]] = {}

    async def connect(self) -> None:
        async def _reconnected_cb() -> None:
            logger.warning(
                "NATS reconnected — re-creating %d known streams", len(self._known_streams)
            )
            for name, (subjects, retention) in list(self._known_streams.items()):
                try:
                    await self._create_stream(name, subjects, retention=retention)
                    logger.info("Re-created stream %s after reconnect", name)
                except Exception as exc:
                    logger.warning(
                        "Failed to re-create stream %s after reconnect: %s", name, exc
                    )

        await self.nc.connect(servers=[self.url], reconnected_cb=_reconnected_cb)
        self.js = self.nc.jetstream()

    async def close(self) -> None:
        try:
            await self.nc.drain()
        finally:
            await self.nc.close()

    async def _create_stream(
        self, name: str, subjects: list[str], *, retention: str = "limits"
    ) -> None:
        """Low-level stream creation — always attempts to create, ignores AlreadyExists."""
        assert self.js is not None
        rp = (
            RetentionPolicy.LIMITS
            if retention == "limits"
            else RetentionPolicy.WORK_QUEUE
        )
        cfg = StreamConfig(
            name=name,
            subjects=subjects,
            retention=rp,
            storage=StorageType.FILE,
            max_msgs=-1,
            max_bytes=-1,
            max_age=0,
        )
        try:
            await self.js.add_stream(cfg)
            logger.info(
                "Created stream %s subjects=%s retention=%s", name, subjects, retention
            )
        except Exception as exc:
            # Stream may already exist — that's fine
            if "already in use" in str(exc).lower() or "exists" in str(exc).lower():
                logger.debug("Stream %s already exists", name)
            else:
                raise

    async def ensure_stream(
        self, name: str, subjects: list[str], *, retention: str = "limits"
    ) -> None:
        assert self.js is not None
        # Remember this stream so we can re-create it after a reconnect
        self._known_streams[name] = (subjects, retention)
        try:
            await self.js.stream_info(name)
            return
        except NotFoundError:
            pass

        await self._create_stream(name, subjects, retention=retention)


    async def ensure_kv_bucket(
        self, bucket: str, *, ttl_seconds: int = 0
    ) -> None:
        """Create the KV bucket if it does not already exist.

        Args:
            bucket:      Bucket name, e.g. ``"COLLECTOR_REGISTRY"``.
            ttl_seconds: If > 0, entries expire after this many seconds.
                         Use 0 (default) for no expiry.
        """
        assert self.js is not None
        try:
            await self.js.key_value(bucket)
            return
        except NotFoundError:
            pass

        ttl = _dt.timedelta(seconds=ttl_seconds) if ttl_seconds > 0 else None
        cfg = KeyValueConfig(bucket=bucket, history=1, ttl=ttl)
        await self.js.create_key_value(cfg)
        logger.info("Created KV bucket %s ttl_seconds=%s", bucket, ttl_seconds or "none")

    async def kv_put(self, bucket: str, key: str, payload: Any) -> None:
        """Serialise *payload* as JSON and store it under *key* in *bucket*."""
        assert self.js is not None
        kv = await self.js.key_value(bucket)
        data = json.dumps(payload, default=str).encode("utf-8")
        await kv.put(key, data)

    async def kv_watch(self, bucket: str):
        """Return a KV watcher that yields all current entries then live updates.

        Yields :class:`nats.js.kv.KeyValueEntry` objects.  The caller should
        inspect ``entry.operation`` to distinguish puts from deletes:

            from nats.js.kv import KeyValueOp
            async for entry in await bus.kv_watch("MY_BUCKET"):
                if entry.operation != KeyValueOp.DEL:
                    ...  # new / updated value
        """
        assert self.js is not None
        kv = await self.js.key_value(bucket)
        return await kv.watchall()

    async def publish_json(self, subject: str, payload: Any) -> None:
        assert self.js is not None
        data = json.dumps(payload, default=str).encode("utf-8")
        await self.js.publish(subject, data)

