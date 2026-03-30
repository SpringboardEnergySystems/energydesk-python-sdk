"""Shared Prometheus metrics for all collector worker PODs.

This module is the single source of truth for the *infrastructure-level*
metrics that every worker exposes regardless of what data it ingests:

  collector_jobs_total          – Counter  (job_type, status)
  collector_job_duration_seconds – Histogram (job_type)
  worker_alive_timestamp_seconds – Gauge   (unix time of last heartbeat)

Workers that need *domain-specific* metrics (e.g. ``syncer_records_synced``)
should declare those Counters/Gauges locally in their own repo.  The
``prometheus_client`` global registry merges all metrics automatically onto
the same ``/metrics`` endpoint — no explicit wiring needed.

Usage::

    from energydeskapi.collector.metrics import (
        JOBS_TOTAL, JOB_DURATION, WORKER_ALIVE, start_metrics_server,
    )

    # At process start, before asyncio.run():
    start_metrics_server(config.metrics_port)

    # In the job dispatch path:
    JOBS_TOTAL.labels(job_type="nordpool.dayahead", status="succeeded").inc()
    JOB_DURATION.labels(job_type="nordpool.dayahead").observe(3.7)

    # In the worker heartbeat loop:
    WORKER_ALIVE.set_to_current_time()
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# ── Prometheus (optional — silent no-op if not installed) ─────────────────
try:
    from prometheus_client import Counter, Gauge, Histogram
    from prometheus_client import start_http_server as _start_http_server

    JOBS_TOTAL = Counter(
        "collector_jobs_total",
        "Total jobs dispatched by the worker loop",
        ["job_type", "status"],
    )
    JOB_DURATION = Histogram(
        "collector_job_duration_seconds",
        "Job handler execution duration in seconds",
        ["job_type"],
    )
    WORKER_ALIVE = Gauge(
        "worker_alive_timestamp_seconds",
        "Unix timestamp of the last pull-loop iteration (heartbeat)",
    )

    _PROMETHEUS_AVAILABLE = True

except ImportError:
    _PROMETHEUS_AVAILABLE = False

    Counter = None          # type: ignore[assignment,misc]
    Gauge = None            # type: ignore[assignment,misc]
    Histogram = None        # type: ignore[assignment,misc]
    _start_http_server = None  # type: ignore[assignment]

    class _Noop:  # type: ignore[no-untyped-def]
        """Drop-in stub used when prometheus_client is not installed."""
        def labels(self, **_kw: object) -> "_Noop": return self
        def inc(self, _n: float = 1) -> None: pass
        def observe(self, _v: float) -> None: pass
        def set(self, _v: float) -> None: pass
        def set_to_current_time(self) -> None: pass

    JOBS_TOTAL = _Noop()      # type: ignore[assignment]
    JOB_DURATION = _Noop()    # type: ignore[assignment]
    WORKER_ALIVE = _Noop()    # type: ignore[assignment]
# ──────────────────────────────────────────────────────────────────────────


def start_metrics_server(port: int) -> None:
    """Expose ``/metrics`` on *port* using the built-in stdlib HTTP server.

    ``prometheus_client.start_http_server`` spawns a single daemon thread —
    no Flask, no uvicorn, no extra overhead.  It is safe to call before
    ``asyncio.run()`` because the metrics thread is completely independent of
    the event loop.

    Passing ``port=0`` is an explicit opt-out: the endpoint is not started and
    no warning is logged.  Workers that want metrics enabled set the
    ``METRICS_PORT`` environment variable (default **8000** in
    ``WorkerConfig``).
    """
    if port == 0:
        logger.debug("METRICS_PORT=0 — Prometheus scrape endpoint disabled")
        return

    if not _PROMETHEUS_AVAILABLE:
        logger.warning(
            "prometheus_client not installed — "
            "Prometheus endpoint NOT started on port %d",
            port,
        )
        return

    _start_http_server(port)
    logger.info("Prometheus /metrics listening on port %d", port)

