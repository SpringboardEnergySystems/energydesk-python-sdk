from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Optional
from uuid import uuid4

from nats.js.kv import KV_DEL, KV_PURGE

from energydeskapi.collector.config import SchedulerConfig
from energydeskapi.collector.models import JobMessage, JobSchedule, WorkerRegistration
from energydeskapi.collector.nats_client import NatsBus
from energydeskapi.collector.protocols import ScheduleTracker

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _idempotency_key(
    job_type: str, partition_key: str, scheduled_for: datetime
) -> str:
    """Deterministic key — must remain stable across restarts."""
    return f"{job_type}|{partition_key}|{scheduled_for.replace(microsecond=0).isoformat()}"


async def _publish_job(
    bus: NatsBus,
    config: SchedulerConfig,
    run_tracker: Optional[ScheduleTracker],
    job_type: str,
    source: str,
    scheduled_for: datetime,
) -> None:
    run_id = str(uuid4())
    created_at = _utcnow()
    partition = "system"
    idem = _idempotency_key(job_type, partition, scheduled_for)

    if run_tracker:
        await run_tracker.create_scheduled(
            run_id=run_id,
            job_type=job_type,
            partition_key=partition,
            scheduled_for=scheduled_for,
            created_at=created_at,
            idempotency_key=idem,
        )

    msg = JobMessage(
        run_id=run_id,
        job_type=job_type,
        source=source,
        scheduled_for=scheduled_for,
        created_at=created_at,
        partition_key=partition,
        idempotency_key=idem,
        params={},
    )

    subject = f"ingest.jobs.{job_type}"
    payload = msg.model_dump() if hasattr(msg, "model_dump") else msg.dict()
    await bus.publish_json(subject, payload)
    logger.info(
        "Scheduled %s run_id=%s for=%s", subject, run_id, scheduled_for.isoformat()
    )


async def _job_loop(
    bus: NatsBus,
    config: SchedulerConfig,
    run_tracker: Optional[ScheduleTracker],
    registration: WorkerRegistration,
) -> None:
    """Cron loop for a single registered job type.  Runs until cancelled."""
    schedule = JobSchedule(cron=registration.cron, timezone=registration.timezone)
    logger.info(
        "Cron loop started: job_type=%s cron=%r tz=%s",
        registration.job_type,
        registration.cron,
        registration.timezone,
    )
    while True:
        now = _utcnow()
        scheduled_for = schedule.next_run_time(now)
        wait_secs = schedule.seconds_until_next(now)
        logger.debug(
            "Next run for %s in %.1f s at %s",
            registration.job_type,
            wait_secs,
            scheduled_for.isoformat(),
        )
        await asyncio.sleep(wait_secs)
        try:
            await _publish_job(
                bus,
                config,
                run_tracker,
                registration.job_type,
                registration.source,
                scheduled_for,
            )
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Failed to publish job %s", registration.job_type)


async def _persist_registration(
    run_tracker: Optional[ScheduleTracker],
    reg: WorkerRegistration,
) -> None:
    """Persist a WorkerRegistration to durable storage if supported."""
    if run_tracker is None:
        return
    upsert = getattr(run_tracker, "upsert_registration", None)
    if upsert is None:
        return
    try:
        await upsert(reg)
    except Exception:
        logger.exception("Failed to persist registration for job_type=%s", reg.job_type)


async def run_scheduler(
    bus: NatsBus,
    config: SchedulerConfig,
    *,
    run_tracker: Optional[ScheduleTracker] = None,
) -> None:
    """Dynamic cron scheduler — driven by NATS KV worker registrations.

    Watches the ``COLLECTOR_REGISTRY`` KV bucket (configured via
    ``config.registry_kv_bucket``).  For every ``WorkerRegistration`` entry
    it finds (or receives as a live update) it starts a dedicated
    :func:`_job_loop` asyncio task.  Deleting a KV entry cancels the
    corresponding loop.

    Workers in any language write their registration JSON into the bucket
    on startup; see :mod:`energydeskapi.collector.worker_registration` for
    the Python helper.

    ``bus`` must already be connected by the caller.
    """
    await bus.ensure_stream(
        config.js_stream_jobs, [config.subject_jobs], retention="workqueue"
    )
    await bus.ensure_kv_bucket(config.registry_kv_bucket)

    # job_type → running asyncio Task
    _tasks: Dict[str, asyncio.Task] = {}

    def _start(reg: WorkerRegistration) -> None:
        job_type = reg.job_type
        existing = _tasks.get(job_type)
        if existing and not existing.done():
            # Re-registration: restart only if cron or tz changed.
            # For simplicity always restart to pick up any update.
            logger.info(
                "Re-registration received for job_type=%s — restarting cron loop",
                job_type,
            )
            existing.cancel()
        _tasks[job_type] = asyncio.create_task(
            _job_loop(bus, config, run_tracker, reg),
            name=f"cron-{job_type}",
        )
        logger.info(
            "Cron loop task created: job_type=%s cron=%s", job_type, reg.cron
        )

    def _stop(job_type: str) -> None:
        task = _tasks.pop(job_type, None)
        if task and not task.done():
            task.cancel()
            logger.info("Cron loop cancelled for job_type=%s (KV entry removed)", job_type)

    logger.info(
        "Scheduler watching KV bucket %r for worker registrations …",
        config.registry_kv_bucket,
    )

    watcher = await bus.kv_watch(config.registry_kv_bucket)
    while True:
        try:
            entry = await watcher.updates(timeout=5.0)
        except Exception:
            # nats.errors.TimeoutError on idle, or transient errors — keep polling.
            continue

        if entry is None:
            # Explicit None: bucket was empty at watch-creation time (init done).
            continue

        if entry.operation in (KV_DEL, KV_PURGE):
            _stop(entry.key)
        else:
            try:
                reg = WorkerRegistration.model_validate_json(entry.value)
            except Exception:
                logger.exception(
                    "Invalid WorkerRegistration in KV key=%s — skipping", entry.key
                )
                continue
            asyncio.create_task(_persist_registration(run_tracker, reg))
            _start(reg)


