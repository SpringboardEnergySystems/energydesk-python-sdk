"""NATS JetStream utility helpers for worker lifecycle management.

Typical usage — skip stale queued jobs at startup so a worker that has been
down for a long time doesn't replay a week's worth of cron triggers:

    from energydeskapi.collector.nats_utils import drain_consumer

    discarded = await drain_consumer(bus, sub, config)
    logger.info("Startup purge: discarded %d stale messages", discarded)

``run_worker`` calls this automatically when ``config.purge_on_startup`` is
``True`` (set via the ``PURGE_ON_STARTUP=true`` environment variable).
"""
from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nats.js.client import PushSubscription, PullSubscription

from energydeskapi.collector.config import WorkerConfig
from energydeskapi.collector.nats_client import NatsBus

logger = logging.getLogger(__name__)


async def drain_consumer(
    bus: NatsBus,
    sub: "PullSubscription",
    config: WorkerConfig,
    *,
    batch_size: int = 200,
) -> int:
    """Fetch and ACK every pending message for this worker's consumer without
    processing it.

    Only messages whose ``job_type`` is in *this* worker's ``config.job_types``
    are silently ACK'd (discarded).  Messages for other job types are NAK'd
    immediately so that the correct worker can still pick them up.

    This is the preferred startup-purge strategy for **work-queue** streams
    (one consumer per worker type) because it does not affect other consumers.

    Args:
        bus:        Connected ``NatsBus`` instance.
        sub:        Already-created pull subscription (created by ``run_worker``
                    before the main loop — passed here to avoid double-creating
                    the durable consumer).
        config:     Worker config; used to resolve ``job_types`` and
                    ``durable_name``.
        batch_size: How many messages to fetch per round-trip.  Larger values
                    reduce round-trips on a very long backlog.

    Returns:
        The number of messages that were silently discarded (ACK'd without
        processing).
    """
    assert bus.js is not None, "NatsBus must be connected before calling drain_consumer"

    selected: set[str] = (
        {j.strip() for j in config.job_types.split(",") if j.strip()}
        if config.job_types.strip()
        else set()   # empty = handle all → discard all
    )

    # How many messages are pending right now?
    try:
        info = await bus.js.consumer_info(config.js_stream_jobs, config.durable_name)
        total_pending = info.num_pending
    except Exception as exc:
        logger.warning("drain_consumer: could not read consumer info: %s", exc)
        return 0

    if total_pending == 0:
        logger.info(
            "drain_consumer: no pending messages for consumer=%s — nothing to purge",
            config.durable_name,
        )
        return 0

    logger.info(
        "drain_consumer: %d pending messages for consumer=%s — purging...",
        total_pending,
        config.durable_name,
    )

    discarded = 0
    remaining = total_pending

    while remaining > 0:
        batch = min(remaining, batch_size)
        try:
            msgs = await sub.fetch(batch=batch, timeout=2.0)
        except (asyncio.TimeoutError, TimeoutError):
            break

        if not msgs:
            break

        for msg in msgs:
            try:
                payload = msg.data.decode("utf-8")
                # Quick check: does this message belong to our job types?
                should_discard = (
                    not selected  # worker handles all → discard all
                    or any(jt in payload for jt in selected)   # fast substring check
                )
                if should_discard:
                    await msg.ack()
                    discarded += 1
                else:
                    # Not ours — put back for the right worker.
                    await msg.nak()
            except Exception as exc:
                logger.warning("drain_consumer: error processing message: %s", exc)
                try:
                    await msg.nak()
                except Exception:
                    pass

        remaining -= len(msgs)

    logger.info(
        "drain_consumer: done — discarded %d / %d pending messages for consumer=%s",
        discarded,
        total_pending,
        config.durable_name,
    )
    return discarded


async def purge_stream_subject(
    bus: NatsBus,
    stream: str,
    subject: str | None = None,
) -> None:
    """Hard-purge all messages from *stream*, optionally filtered by *subject*.

    This uses the NATS JetStream ``purge_stream`` management API which deletes
    messages server-side in a single call — much faster than fetch+ACK for very
    large backlogs.

    .. warning::
        This affects **all consumers** on the stream, not just the calling
        worker.  Prefer :func:`drain_consumer` when multiple workers share the
        same stream.  Use this only when you own the entire stream (e.g. during
        integration tests or single-consumer deployments).

    Args:
        bus:     Connected ``NatsBus`` instance.
        stream:  Name of the JetStream stream to purge.
        subject: Optional subject filter.  When given, only messages published
                 to this exact subject are removed (wildcards supported).
                 When ``None`` the entire stream is purged.
    """
    assert bus.js is not None, "NatsBus must be connected before calling purge_stream_subject"

    try:
        if subject:
            await bus.js.purge_stream(stream, subject=subject)
            logger.info("purge_stream_subject: purged stream=%s subject=%s", stream, subject)
        else:
            await bus.js.purge_stream(stream)
            logger.info("purge_stream_subject: purged entire stream=%s", stream)
    except Exception as exc:
        logger.error(
            "purge_stream_subject: failed to purge stream=%s subject=%s: %s",
            stream,
            subject,
            exc,
        )
        raise

