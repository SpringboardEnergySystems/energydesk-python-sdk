from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable, Protocol, runtime_checkable


@runtime_checkable
class InfluxSink(Protocol):
    """Structural protocol satisfied by InfluxStore (and any test double).

    Only the one method that job handlers actually need is declared here so
    the SDK carries no hard dependency on ``influxdb-client``.
    """

    async def write_points(self, points: Iterable[Any]) -> None: ...


class RunTracker(Protocol):
    """Tracks job-execution lifecycle in a durable store (e.g. Postgres).

    Used by the worker runner.  ``PgStore`` in the collector service
    satisfies this protocol structurally.
    """

    async def already_succeeded(self, idempotency_key: str) -> bool: ...

    async def mark_started(self, run_id: str, ts: datetime) -> None: ...

    async def mark_finished(
        self,
        run_id: str,
        ts: datetime,
        status: str,
        *,
        error: str | None = None,
        metrics: Any = None,
    ) -> None: ...


class ScheduleTracker(Protocol):
    """Records scheduled-job intent before it is published to NATS.

    Used by the scheduler runner.  ``PgStore`` satisfies this structurally.
    """

    async def create_scheduled(
        self,
        *,
        run_id: str,
        job_type: str,
        partition_key: str,
        scheduled_for: datetime,
        created_at: datetime,
        idempotency_key: str,
    ) -> None: ...

