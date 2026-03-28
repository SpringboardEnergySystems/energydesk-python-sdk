from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from energydeskapi.collector.config import SchedulerConfig
from energydeskapi.collector.jobs import registry as job_registry
from energydeskapi.collector.jobs.registry import JobDef
from energydeskapi.collector.models import JobMessage
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
    job_def: JobDef,
    scheduled_for: datetime,
) -> None:
    run_id = str(uuid4())
    created_at = _utcnow()
    partition = "system"
    idem = _idempotency_key(job_def.job_type, partition, scheduled_for)

    if run_tracker:
        await run_tracker.create_scheduled(
            run_id=run_id,
            job_type=job_def.job_type,
            partition_key=partition,
            scheduled_for=scheduled_for,
            created_at=created_at,
            idempotency_key=idem,
        )

    msg = JobMessage(
        run_id=run_id,
        job_type=job_def.job_type,
        source=job_def.source,
        scheduled_for=scheduled_for,
        created_at=created_at,
        partition_key=partition,
        idempotency_key=idem,
        params={},
    )

    subject = f"ingest.jobs.{job_def.job_type}"
    payload = msg.model_dump() if hasattr(msg, "model_dump") else msg.dict()
    await bus.publish_json(subject, payload)
    logger.info(
        "Scheduled %s run_id=%s for=%s", subject, run_id, scheduled_for.isoformat()
    )


async def _job_loop(
    bus: NatsBus,
    config: SchedulerConfig,
    run_tracker: Optional[ScheduleTracker],
    job_def: JobDef,
) -> None:
    schedule = job_def.schedule
    logger.info(
        "Job loop started: job_type=%s cron=%r tz=%s",
        job_def.job_type,
        schedule.cron,
        schedule.timezone,
    )
    while True:
        now = _utcnow()
        scheduled_for = schedule.next_run_time(now)
        wait_secs = schedule.seconds_until_next(now)
        logger.debug(
            "Next run for %s in %.1f s at %s",
            job_def.job_type,
            wait_secs,
            scheduled_for.isoformat(),
        )
        await asyncio.sleep(wait_secs)
        try:
            await _publish_job(bus, config, run_tracker, job_def, scheduled_for)
        except Exception:
            logger.exception("Failed to publish job %s", job_def.job_type)


async def run_scheduler(
    bus: NatsBus,
    config: SchedulerConfig,
    *,
    run_tracker: Optional[ScheduleTracker] = None,
) -> None:
    """Cron-based scheduler loop.

    ``bus`` must already be connected by the caller.  The caller is also
    responsible for closing ``bus`` (and ``run_tracker``) on shutdown.

    Args:
        bus:         Connected ``NatsBus`` instance.
        config:      NATS/stream parameters — no storage credentials.
        run_tracker: Optional store that records every scheduled intent
                     (e.g. ``PgStore``).  When ``None`` jobs are published
                     without a durable record.
    """
    await bus.ensure_stream(
        config.js_stream_jobs, [config.subject_jobs], retention="workqueue"
    )

    scheduled_jobs = [
        job_registry.get(jt)
        for jt in job_registry.list_job_types()
        if job_registry.get(jt) and job_registry.get(jt).schedule is not None
    ]

    if not scheduled_jobs:
        logger.warning(
            "No jobs with a schedule are registered. "
            "Attach a JobSchedule to your JobDef entries in the registry."
        )
        while True:
            await asyncio.sleep(60)

    await asyncio.gather(
        *[_job_loop(bus, config, run_tracker, jd) for jd in scheduled_jobs]
    )

