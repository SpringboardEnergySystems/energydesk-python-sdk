from __future__ import annotations

"""Central event listener — subscribes to INGEST_EVENTS and syncs run status to storage.

Typical usage: run alongside ``run_scheduler()`` in the central scheduler pod so
that run-ledger rows (inserted as ``scheduled`` by the scheduler) are updated to
``running`` / ``succeeded`` / ``failed`` as workers emit ``ingest.runs.*`` events.

    async def run_scheduler() -> None:
        bus = NatsBus(settings.nats_url)
        pg  = PgStore(settings.postgres_dsn)
        await bus.connect()
        await pg.connect()
        try:
            await asyncio.gather(
                _run_scheduler(bus, settings, run_tracker=pg),
                run_event_listener(bus, settings, run_tracker=pg),
            )
        finally:
            await pg.close()
            await bus.close()
"""

import asyncio
import logging

from nats.js.api import ConsumerConfig

from energydeskapi.collector.config import WorkerConfig
from energydeskapi.collector.models import RunEvent
from energydeskapi.collector.nats_client import NatsBus
from energydeskapi.collector.protocols import RunTracker

logger = logging.getLogger(__name__)

# Durable consumer name for the event listener.
# A separate durable from the job-worker consumer so the two don't interfere.
_DURABLE_NAME = "collector-event-listener"


async def run_event_listener(
    bus: NatsBus,
    config: WorkerConfig,
    *,
    run_tracker: RunTracker,
) -> None:
    """Pull-based consumer that translates NATS run events into run-tracker calls.

    Subscribes to ``ingest.runs.*`` on the ``INGEST_EVENTS`` stream with a
    dedicated durable consumer (``collector-event-listener``) so no events are
    lost across restarts.

    Event → RunTracker mapping
    --------------------------
    * ``started``              → ``mark_started(run_id, ts)``
    * ``succeeded`` / ``failed`` / ``dlq``  → ``mark_finished(run_id, ts, status, …)``

    Args:
        bus:         Connected :class:`NatsBus` instance (shared with the scheduler).
        config:      :class:`WorkerConfig` (or any subclass) supplying stream names.
        run_tracker: Durable store to update — typically :class:`PgStore`.
    """
    await bus.ensure_stream(
        config.js_stream_events,
        ["ingest.runs.*", "ingest.dlq"],
        retention="limits",
        max_age_seconds=86_400,       # keep events for 1 day
        max_bytes=268_435_456,        # 256 MiB cap
    )

    js = bus.js
    assert js is not None

    sub = await js.pull_subscribe(
        subject="ingest.runs.*",
        durable=_DURABLE_NAME,
        stream=config.js_stream_events,
        config=ConsumerConfig(
            ack_wait=30,       # ACK within 30 s — events are tiny, should be instant
            max_deliver=5,     # don't loop forever on a bad message
        ),
    )

    logger.info(
        "Event listener started — stream=%s durable=%s",
        config.js_stream_events,
        _DURABLE_NAME,
    )

    while True:
        try:
            msgs = await sub.fetch(batch=100, timeout=1.0)
        except (asyncio.TimeoutError, TimeoutError):
            continue
        except Exception as exc:
            logger.warning(
                "Event listener fetch error (%s: %s) — backing off 5 s before retry",
                type(exc).__name__,
                exc,
            )
            await asyncio.sleep(5)
            continue

        for msg in msgs:
            try:
                event = RunEvent.model_validate_json(msg.data.decode("utf-8"))
            except Exception as exc:
                logger.warning("Unparseable RunEvent — discarding: %s", exc)
                await msg.ack()
                continue

            try:
                if event.status == "started":
                    await run_tracker.mark_started(event.run_id, event.ts)
                    logger.debug(
                        "run_id=%s  status=started", event.run_id
                    )
                elif event.status in ("succeeded", "failed", "dlq"):
                    metrics = event.metrics if event.metrics else None
                    await run_tracker.mark_finished(
                        event.run_id,
                        event.ts,
                        event.status,
                        error=event.error,
                        metrics=metrics,
                    )
                    logger.debug(
                        "run_id=%s  status=%s  metrics=%s",
                        event.run_id, event.status, metrics,
                    )
                else:
                    logger.debug(
                        "run_id=%s  unknown status=%r — ignoring",
                        event.run_id, event.status,
                    )
            except Exception as exc:
                logger.warning(
                    "Failed to update run_tracker for run_id=%s status=%s: %s",
                    event.run_id, event.status, exc,
                )
                # Still ACK so we don't reprocess indefinitely on a DB blip.
                # The run row may simply remain in its last known state.

            await msg.ack()

