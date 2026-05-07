from __future__ import annotations

import asyncio
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
        self._known_streams: dict[str, tuple[list[str], str, int, int]] = {}

    async def connect(
        self,
        *,
        max_attempts: int = 12,
        base_delay: float = 5.0,
        max_delay: float = 60.0,
    ) -> None:
        """Connect to NATS with exponential-backoff retry.

        DNS resolution failures (``socket.gaierror``) and general
        ``OSError`` / ``TimeoutError`` exceptions that occur on the *initial*
        connection attempt are retried up to *max_attempts* times so that
        transient network blips at pod-startup time do not crash the worker.

        Args:
            max_attempts: Maximum number of connection attempts (default 12,
                          i.e. ~10 minutes total with the default delays).
            base_delay:   Initial back-off delay in seconds (default 5 s).
            max_delay:    Maximum back-off delay in seconds (default 60 s).
        """
        async def _reconnected_cb() -> None:
            logger.warning(
                "NATS reconnected — re-creating %d known streams", len(self._known_streams)
            )
            for name, (subjects, retention, max_age_seconds, max_bytes) in list(self._known_streams.items()):
                try:
                    await self._create_stream(
                        name, subjects,
                        retention=retention,
                        max_age_seconds=max_age_seconds,
                        max_bytes=max_bytes,
                    )
                    logger.info("Re-created stream %s after reconnect", name)
                except Exception as exc:
                    logger.warning(
                        "Failed to re-create stream %s after reconnect: %s", name, exc
                    )

        attempt = 0
        delay = base_delay
        while True:
            attempt += 1
            try:
                await self.nc.connect(servers=[self.url], reconnected_cb=_reconnected_cb)
                self.js = self.nc.jetstream()
                if attempt > 1:
                    logger.info("NATS connected after %d attempt(s)", attempt)
                return
            except Exception as exc:
                if attempt >= max_attempts:
                    logger.error(
                        "NATS connection failed after %d attempt(s), giving up: %s",
                        attempt, exc,
                    )
                    raise
                logger.warning(
                    "NATS connection attempt %d/%d failed (%s: %s) — retrying in %.0f s",
                    attempt, max_attempts, type(exc).__name__, exc, delay,
                )
                await asyncio.sleep(delay)
                # Re-create the underlying NATS client instance because the
                # nats-py client may be in a broken state after a failed connect.
                self.nc = NATS()
                delay = min(delay * 2, max_delay)

    async def close(self) -> None:
        try:
            await self.nc.drain()
        finally:
            await self.nc.close()

    async def _create_stream(
        self,
        name: str,
        subjects: list[str],
        *,
        retention: str = "limits",
        max_age_seconds: int = 0,
        max_bytes: int = -1,
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
            max_bytes=max_bytes,
            max_age=max_age_seconds,  # seconds as int; 0 = unlimited
        )
        try:
            await self.js.add_stream(cfg)
            logger.info(
                "Created stream %s subjects=%s retention=%s max_age_seconds=%s max_bytes=%s",
                name, subjects, retention, max_age_seconds or "unlimited", max_bytes if max_bytes > 0 else "unlimited",
            )
        except Exception as exc:
            # Stream may already exist — that's fine
            if "already in use" in str(exc).lower() or "exists" in str(exc).lower():
                logger.debug("Stream %s already exists", name)
            else:
                raise

    async def _update_stream(
        self,
        name: str,
        subjects: list[str],
        *,
        retention: str = "limits",
        max_age_seconds: int = 0,
        max_bytes: int = -1,
    ) -> None:
        """Update an existing stream's limits.  Silently ignores failures so a
        permission error or a version of NATS that rejects the update does not
        prevent the worker from starting."""
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
            max_bytes=max_bytes,
            max_age=max_age_seconds,  # seconds as int; 0 = unlimited
        )
        try:
            await self.js.update_stream(cfg)
            logger.info(
                "Updated stream %s max_age_seconds=%s max_bytes=%s",
                name, max_age_seconds or "unlimited", max_bytes if max_bytes > 0 else "unlimited",
            )
        except Exception as exc:
            logger.warning("Could not update stream %s config: %s", name, exc)

    async def ensure_stream(
        self,
        name: str,
        subjects: list[str],
        *,
        retention: str = "limits",
        max_age_seconds: int = 0,
        max_bytes: int = -1,
    ) -> None:
        assert self.js is not None
        # Remember this stream (with limits) so it can be re-created after a NATS reconnect
        self._known_streams[name] = (subjects, retention, max_age_seconds, max_bytes)
        try:
            info = await self.js.stream_info(name)
            # Stream exists — update limits (e.g. tighter max_bytes / max_age).
            # MERGE new subjects into the existing list so that a new worker
            # can register its subject without losing subjects already in the
            # stream.  An existing wildcard (e.g. "ingest.jobs.>") is preserved
            # because merging keeps all existing entries; a specific subject
            # that is already covered by the wildcard is redundant but harmless.
            existing = list((info.config.subjects or []) if info.config else [])
            merged = existing.copy()
            for s in subjects:
                if s not in merged:
                    merged.append(s)
            await self._update_stream(
                name, merged,
                retention=retention,
                max_age_seconds=max_age_seconds,
                max_bytes=max_bytes,
            )
        except NotFoundError:
            await self._create_stream(
                name, subjects,
                retention=retention,
                max_age_seconds=max_age_seconds,
                max_bytes=max_bytes,
            )


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

    async def kv_get_all(self, bucket: str) -> list[dict]:
        """Return all current (non-deleted) entries in *bucket* as parsed JSON dicts.

        Returns an empty list if the bucket does not exist or is empty.
        """
        assert self.js is not None
        try:
            kv = await self.js.key_value(bucket)
            keys = await kv.keys()
        except Exception:
            return []
        results = []
        for key in keys:
            try:
                entry = await kv.get(key)
                if entry and entry.value:
                    results.append(json.loads(entry.value.decode("utf-8")))
            except Exception:
                logger.debug("Could not read KV entry %s/%s", bucket, key)
        return results

    async def publish_json(self, subject: str, payload: Any) -> None:
        assert self.js is not None
        data = json.dumps(payload, default=str).encode("utf-8")
        await self.js.publish(subject, data)

