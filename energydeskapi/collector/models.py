from __future__ import annotations

import os
import socket
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from zoneinfo import ZoneInfo

from croniter import croniter
from pydantic import BaseModel, Field, validator


class JobSchedule(BaseModel):
    """Cron-based schedule declaration attached to a JobDef.

    ``cron`` follows the standard 5-field cron syntax::

        ┌─────── minute  (0-59)
        │ ┌───── hour    (0-23)
        │ │ ┌─── dom     (1-31)
        │ │ │ ┌─ month   (1-12)
        │ │ │ │ ┌ dow    (0-7, both 0 and 7 = Sunday)
        │ │ │ │ │
        * * * * *

    Examples::

        "*/15 * * * *"   – every 15 minutes
        "0 * * * *"      – every hour on the hour
        "0 14 * * 1-5"   – 14:00 on weekdays
        "5 13 * * *"     – 13:05 every day (Nord Pool day-ahead release)
    """

    cron: str
    timezone: str = "Europe/Oslo"

    @validator("cron")
    @classmethod
    def _valid_cron(cls, v: str) -> str:
        if not croniter.is_valid(v):
            raise ValueError(f"Invalid cron expression: {v!r}")
        return v

    def next_run_time(self, now: Optional[datetime] = None) -> datetime:
        """Return the next fire time as a timezone-aware UTC datetime."""
        tz = ZoneInfo(self.timezone)
        base = (now or datetime.now(timezone.utc)).astimezone(tz)
        it = croniter(self.cron, base)
        next_dt: datetime = it.get_next(datetime)
        if next_dt.tzinfo is None:
            next_dt = next_dt.replace(tzinfo=tz)
        return next_dt.astimezone(timezone.utc)

    def seconds_until_next(self, now: Optional[datetime] = None) -> float:
        """Return the number of seconds until the next scheduled fire time."""
        _now = now or datetime.now(timezone.utc)
        return max(0.0, (self.next_run_time(_now) - _now).total_seconds())


class JobMessage(BaseModel):
    run_id: str
    job_type: str
    source: str
    scheduled_for: datetime
    created_at: datetime
    partition_key: str = "system"
    idempotency_key: str
    params: Dict[str, Any] = Field(default_factory=dict)


class RunEvent(BaseModel):
    run_id: str
    job_type: str
    partition_key: str
    status: str  # started|succeeded|failed|dlq
    ts: datetime
    metrics: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


def _default_worker_id() -> str:
    """Stable within a process: hostname + PID."""
    return f"{socket.gethostname()}-{os.getpid()}"


class WorkerRegistration(BaseModel):
    """Language-agnostic registration record published by workers into NATS KV.

    Workers in any language write this as JSON into the ``COLLECTOR_REGISTRY``
    KV bucket (key = ``job_type``) on startup.  The central collector scheduler
    watches the bucket and builds its cron schedule dynamically from these
    entries.

    Fields
    ------
    job_type:
        Unique identifier, e.g. ``"nordpool.dayahead"``.  Used as the NATS
        subject suffix (``ingest.jobs.<job_type>``) and the KV bucket key.
    source:
        Human-readable source label, e.g. ``"nordpool"``.
    cron:
        Standard 5-field cron expression, e.g. ``"5 13 * * *"``.
    timezone:
        IANA timezone name for cron evaluation, default ``"Europe/Oslo"``.
    worker_id:
        Unique identifier for this worker process/pod.  Auto-generated from
        hostname + PID if not supplied.
    registered_at:
        UTC timestamp written (and refreshed on each heartbeat) by the worker.
    heartbeat_interval_seconds:
        How often the worker refreshes the KV entry.  The scheduler portal
        uses ``registered_at`` to flag stale workers.
    metadata:
        Arbitrary extra fields (version, git SHA, k8s pod name, …).
    """

    job_type: str
    source: str
    cron: str
    timezone: str = "Europe/Oslo"
    worker_id: str = Field(default_factory=_default_worker_id)
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    heartbeat_interval_seconds: int = 120
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator("cron")
    @classmethod
    def _valid_cron(cls, v: str) -> str:
        if not croniter.is_valid(v):
            raise ValueError(f"Invalid cron expression: {v!r}")
        return v

