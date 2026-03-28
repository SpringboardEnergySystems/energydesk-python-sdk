from __future__ import annotations

import json
import logging
from typing import Any, Callable, Optional

from nats.aio.client import Client as NATS
from nats.js.api import RetentionPolicy, StorageType, StreamConfig
from nats.js.errors import NotFoundError

logger = logging.getLogger(__name__)


class NatsBus:
    def __init__(self, url: str):
        self.url = url
        self.nc = NATS()
        self.js = None

    async def connect(self) -> None:
        await self.nc.connect(servers=[self.url])
        self.js = self.nc.jetstream()

    async def close(self) -> None:
        try:
            await self.nc.drain()
        finally:
            await self.nc.close()

    async def ensure_stream(
        self, name: str, subjects: list[str], *, retention: str = "limits"
    ) -> None:
        assert self.js is not None
        try:
            await self.js.stream_info(name)
            return
        except NotFoundError:
            pass

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
        await self.js.add_stream(cfg)
        logger.info(
            "Created stream %s for subjects=%s retention=%s", name, subjects, retention
        )

    async def publish_json(self, subject: str, payload: Any) -> None:
        assert self.js is not None
        data = json.dumps(payload, default=str).encode("utf-8")
        await self.js.publish(subject, data)

