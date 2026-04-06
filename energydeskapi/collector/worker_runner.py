from __future__ import annotations

import asyncio
import logging
import time as _time
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from nats.js.api import ConsumerConfig

from energydeskapi.collector.config import WorkerConfig
from energydeskapi.collector.jobs.registry import get, list_job_types
from energydeskapi.collector.metrics import JOB_DURATION, JOBS_TOTAL, WORKER_ALIVE
from energydeskapi.collector.models import JobMessage, RunEvent
from energydeskapi.collector.nats_client import NatsBus
from energydeskapi.collector.protocols import RunTracker
from energydeskapi.collector.sinks import SinkBundle

logger = logging.getLogger(__name__)



def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


async def drain_consumer(bus: NatsBus, sub: Any, config: WorkerConfig) -> int:
    """ACK and discard every pending message for this consumer.

    Used on startup to throw away a backlog of stale / repeatedly-failed jobs
    so the worker enters the main loop with a clean slate.  Only appropriate
    for workers whose jobs are time-sensitive and should not be processed after
    a delay (e.g. forward-curve generation).

    Returns:
        Number of messages discarded.
    """
    discarded = 0
    while True:
        try:
            msgs = await sub.fetch(batch=100, timeout=1.0)
            for msg in msgs:
                try:
                    await msg.ack()
                except Exception:
                    pass
                discarded += 1
        except (asyncio.TimeoutError, TimeoutError):
            break
    return discarded


async def run_worker(
    bus: NatsBus,
    config: WorkerConfig,
    *,
    run_tracker: Optional[RunTracker] = None,
    sinks: Optional[SinkBundle] = None,
) -> None:
    """Pull-based worker loop.

    ``bus`` must already be connected by the caller.  The caller is also
    responsible for closing ``bus`` (and any stores in ``sinks``) after this
    coroutine returns or is cancelled.

    Args:
        bus:         Connected ``NatsBus`` instance.
        config:      NATS/stream parameters — no storage credentials.
        run_tracker: Optional durable run-lifecycle store (e.g. ``PgStore``).
                     When ``None`` idempotency checking and status tracking
                     are skipped.
        sinks:       Bundle of optional domain-data sinks forwarded to every
                     job handler.  Defaults to an empty ``SinkBundle``.
    """
    if sinks is None:
        sinks = SinkBundle()

    if config.job_types.strip():
        selected: set[str] = {j.strip() for j in config.job_types.split(",") if j.strip()}
        logger.info(
            "Worker starting in FILTERED mode – handling job types: %s", sorted(selected)
        )
    else:
        selected = set(list_job_types())
        logger.info(
            "Worker starting in ALL-JOBS mode – %d registered job types: %s",
            len(selected),
            sorted(selected),
        )

    await bus.ensure_stream(
        config.js_stream_jobs, [config.subject_jobs],
        retention="workqueue",
        max_age_seconds=86_400,      # 24 h  — jobs are consumed immediately
        max_bytes=536_870_912,       # 512 MiB
    )
    await bus.ensure_stream(
        config.js_stream_events,
        ["ingest.runs.*", "ingest.dlq"],
        retention="limits",
        max_age_seconds=86_400,      # 1 day  — was 7 days; keeps disk use bounded
        max_bytes=268_435_456,       # 256 MiB — was 2 GiB; prevent PVC saturation
    )

    js = bus.js
    assert js is not None

    sub = await js.pull_subscribe(
        subject=config.subject_jobs,
        durable=config.durable_name,
        stream=config.js_stream_jobs,
        config=ConsumerConfig(
            # Workers must ACK within this window or NATS redelivers.
            # Must be longer than the slowest expected job (forward-curve ~2 min).
            ack_wait=timedelta(seconds=config.ack_wait_seconds),
            # Stop redelivering after this many attempts; message goes to DLQ.
            max_deliver=config.max_deliver,
        ),
    )

    if config.purge_on_startup:
        logger.info(
            "PURGE_ON_STARTUP=true — draining stale messages for consumer=%s",
            config.durable_name,
        )
        discarded = await drain_consumer(bus, sub, config)
        logger.info("Startup purge complete: %d messages discarded", discarded)

    sem = asyncio.Semaphore(config.worker_concurrency)

    async def handle_one(msg: Any) -> None:
        async with sem:
            # ── parse ──────────────────────────────────────────────────
            try:
                job = JobMessage.model_validate_json(msg.data.decode("utf-8"))
            except Exception as exc:
                logger.exception("Unparseable job message: %s", exc)
                await msg.ack()
                return

            # ── filter ─────────────────────────────────────────────────
            if job.job_type not in selected:
                logger.debug(
                    "Skipping job_type=%s (not in selected) – NAK for redelivery",
                    job.job_type,
                )
                try:
                    await msg.nak()
                except Exception:
                    await msg.ack()
                return

            # ── idempotency ────────────────────────────────────────────
            if run_tracker and await run_tracker.already_succeeded(job.idempotency_key):
                logger.info(
                    "Skipping already-succeeded idempotency_key=%s", job.idempotency_key
                )
                await msg.ack()
                return

            # ── start ──────────────────────────────────────────────────
            started = _utcnow()
            if run_tracker:
                await run_tracker.mark_started(job.run_id, started)

            await bus.publish_json(
                "ingest.runs.started",
                RunEvent(
                    run_id=job.run_id,
                    job_type=job.job_type,
                    partition_key=job.partition_key,
                    status="started",
                    ts=started,
                ).model_dump(),
            )

            # ── dispatch ───────────────────────────────────────────────
            jobdef = get(job.job_type)
            if jobdef is None:
                logger.warning("No handler registered for job_type=%s", job.job_type)
                await msg.ack()
                return

            t0 = _time.monotonic()
            try:
                metrics = await jobdef.handler(job, sinks)
                duration = _time.monotonic() - t0

                JOBS_TOTAL.labels(job_type=job.job_type, status="succeeded").inc()
                JOB_DURATION.labels(job_type=job.job_type).observe(duration)

                finished = _utcnow()
                if run_tracker:
                    await run_tracker.mark_finished(
                        job.run_id, finished, "succeeded", metrics=metrics
                    )
                await bus.publish_json(
                    "ingest.runs.succeeded",
                    RunEvent(
                        run_id=job.run_id,
                        job_type=job.job_type,
                        partition_key=job.partition_key,
                        status="succeeded",
                        ts=finished,
                        metrics=metrics,
                    ).model_dump(),
                )
                await msg.ack()

            except Exception as exc:
                duration = _time.monotonic() - t0

                JOBS_TOTAL.labels(job_type=job.job_type, status="failed").inc()
                JOB_DURATION.labels(job_type=job.job_type).observe(duration)

                logger.exception(
                    "Job failed run_id=%s job_type=%s", job.run_id, job.job_type
                )
                finished = _utcnow()
                if run_tracker:
                    await run_tracker.mark_finished(
                        job.run_id, finished, "failed", error=str(exc)
                    )
                await bus.publish_json(
                    "ingest.runs.failed",
                    RunEvent(
                        run_id=job.run_id,
                        job_type=job.job_type,
                        partition_key=job.partition_key,
                        status="failed",
                        ts=finished,
                        error=str(exc),
                    ).model_dump(),
                )
                try:
                    # Delay redelivery to prevent a tight CPU spin when a job
                    # keeps failing (e.g. bad credentials, unreachable API).
                    # 30 s gives the external service time to recover without
                    # hammering NATS or flooding the events stream.
                    await msg.nak(delay=timedelta(seconds=30))
                except Exception:
                    await msg.ack()

    # ── main pull loop ─────────────────────────────────────────────────────
    while True:
        WORKER_ALIVE.set_to_current_time()
        try:
            msgs = await sub.fetch(batch=50, timeout=1.0)
        except (asyncio.TimeoutError, TimeoutError):
            continue
        await asyncio.gather(*(handle_one(m) for m in msgs))
