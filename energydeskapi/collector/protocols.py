from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable, Optional, Protocol, runtime_checkable


@runtime_checkable
class InfluxSink(Protocol):
    """Structural protocol satisfied by InfluxStore (and any test double).

    Only the one method that job handlers actually need is declared here so
    the SDK carries no hard dependency on ``influxdb-client``.
    """

    async def write_points(self, points: Iterable[Any]) -> None: ...


@runtime_checkable
class PostgresSink(Protocol):
    """Minimal async Postgres interface for job handlers.

    Mirrors the subset of ``asyncpg.Pool`` / ``asyncpg.Connection`` that
    handlers need for domain-data writes and reads.  The concrete ``PgStore``
    in the collector service satisfies this protocol structurally (it exposes
    ``execute``, ``fetch``, and ``fetchrow`` delegating to its pool).
    """

    async def execute(self, sql: str, *args: Any) -> str: ...

    async def fetch(self, sql: str, *args: Any) -> list[Any]: ...

    async def fetchrow(self, sql: str, *args: Any) -> Optional[Any]: ...


@runtime_checkable
class ApiSink(Protocol):
    """Minimal interface for handlers that write/read via the Energydesk REST API.

    Satisfied structurally by ``energydeskapi.sdk.api_connection.ApiConnection``
    (and ``ApiTempConnection``).  Declared as a Protocol so handlers stay
    testable without needing a live API server.

    Build the connection in your entry-point factory::

        api_conn = ApiConnection(url)
        api_conn.set_token(tok, "Token")
        sinks = SinkBundle(api=api_conn)
    """

    def get_base_url(self) -> str: ...

    def exec_get_url(
        self,
        trailing_url: str,
        parameters: dict = ...,
        extra_headers: dict = ...,
    ) -> "dict | list | str | None": ...

    def exec_post_url(
        self,
        trailing_url: str,
        payload: dict,
        extra_headers: dict = ...,
    ) -> "tuple[bool, list | str | None, int, str | None]": ...

    def exec_patch_url(
        self,
        trailing_url: str,
        payload: dict,
        extra_headers: dict = ...,
    ) -> "tuple[bool, list | str | None, int, str | None]": ...

    def exec_delete_url(
        self,
        trailing_url: str,
        extra_headers: dict = ...,
    ) -> "tuple[bool, list | str | None, int, str | None]": ...


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

