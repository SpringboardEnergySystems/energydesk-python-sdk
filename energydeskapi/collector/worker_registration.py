from __future__ import annotations

"""Helper for worker processes to register themselves with the central scheduler.

Usage (Python workers)::

    from energydeskapi.collector.worker_registration import register_worker
    from energydeskapi.collector.models import WorkerRegistration

    reg = WorkerRegistration(
        job_type="nordpool.dayahead",
        source="nordpool",
        cron="5 13 * * *",
        timezone="Europe/Oslo",
    )
    heartbeat_task = await register_worker(bus, config, reg)
    # then run your worker loop:
    await run_worker(bus, config, sinks=sinks)

Non-Python workers publish the same JSON directly to the NATS KV bucket
``COLLECTOR_REGISTRY`` (key = job_type) and refresh the entry periodically.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

from energydeskapi.collector.config import SchedulerConfig
from energydeskapi.collector.models import WorkerRegistration
from energydeskapi.collector.nats_client import NatsBus

logger = logging.getLogger(__name__)


async def register_worker(
    bus: NatsBus,
    config: SchedulerConfig,
    registration: WorkerRegistration,
    *,
    start_heartbeat: bool = True,
) -> Optional[asyncio.Task]:
    """Write *registration* into the NATS KV registry bucket.

    The KV key is ``registration.job_type``; the value is the JSON-serialised
    ``WorkerRegistration``.  The central collector scheduler watches this
    bucket and starts a cron loop for each registered job_type.

    Args:
        bus:             Connected :class:`NatsBus` instance.
        config:          Scheduler config — used to resolve the KV bucket name.
        registration:    The worker's self-description (job_type, cron, …).
        start_heartbeat: When ``True`` (default) a background asyncio task is
                         created that refreshes the KV entry every
                         ``registration.heartbeat_interval_seconds`` seconds,
                         updating ``registered_at`` each time.  The returned
                         task should be cancelled on graceful shutdown.

    Returns:
        The heartbeat :class:`asyncio.Task` if ``start_heartbeat=True``,
        otherwise ``None``.
    """
    await bus.ensure_kv_bucket(config.registry_kv_bucket)
    await _put(bus, config.registry_kv_bucket, registration)
    logger.info(
        "Registered job_type=%s cron=%r worker_id=%s",
        registration.job_type,
        registration.cron,
        registration.worker_id,
    )

    if not start_heartbeat:
        return None

    async def _heartbeat() -> None:
        while True:
            await asyncio.sleep(registration.heartbeat_interval_seconds)
            try:
                now = datetime.now(timezone.utc)
                # Pydantic v2: model_copy; v1: copy
                if hasattr(registration, "model_copy"):
                    refreshed = registration.model_copy(update={"registered_at": now})
                else:
                    refreshed = registration.copy(update={"registered_at": now})
                await _put(bus, config.registry_kv_bucket, refreshed)
                logger.debug("Heartbeat refreshed for job_type=%s", registration.job_type)
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception(
                    "Heartbeat failed for job_type=%s", registration.job_type
                )

    task = asyncio.create_task(
        _heartbeat(), name=f"heartbeat-{registration.job_type}"
    )
    return task


async def _put(bus: NatsBus, bucket: str, reg: WorkerRegistration) -> None:
    payload = reg.model_dump() if hasattr(reg, "model_dump") else reg.dict()
    await bus.kv_put(bucket, reg.job_type, payload)

