from __future__ import annotations

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
