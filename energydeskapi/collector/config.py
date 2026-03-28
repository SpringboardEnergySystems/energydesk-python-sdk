from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SchedulerConfig(BaseSettings):
    """Minimal config for a scheduler — only the fields needed to publish jobs.

    This is the base of the config hierarchy:

        SchedulerConfig          ← scheduler pod (just NATS + stream names)
            └── WorkerConfig     ← worker pod (adds consumer / concurrency fields)
                    └── Settings ← full collector service (adds Influx, Postgres, portal)
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    nats_url: str = Field(default="nats://nats:4222", alias="NATS_URL")
    js_stream_jobs: str = Field(default="INGEST_JOBS", alias="JS_STREAM_JOBS")
    subject_jobs: str = Field(default="ingest.jobs.>", alias="SUBJECT_JOBS")


class WorkerConfig(SchedulerConfig):
    """Config for a worker pod.

    Extends ``SchedulerConfig`` so a ``WorkerConfig`` instance can be passed
    directly to both ``run_scheduler`` and ``run_worker`` — useful for thin
    pods (e.g. the syncer) that run both roles in one process.
    """

    js_stream_events: str = Field(default="INGEST_EVENTS", alias="JS_STREAM_EVENTS")

    subject_runs: str = Field(default="ingest.runs.*", alias="SUBJECT_RUNS")
    subject_dlq: str = Field(default="ingest.dlq", alias="SUBJECT_DLQ")

    durable_name: str = Field(default="collector-workers", alias="DURABLE_NAME")
    ack_wait_seconds: int = Field(default=60, alias="ACK_WAIT_SECONDS")
    max_deliver: int = Field(default=10, alias="MAX_DELIVER")
    worker_concurrency: int = Field(default=4, alias="WORKER_CONCURRENCY")

    # Comma-separated list of job_types to handle; empty = all registered.
    job_types: str = Field(default="", alias="JOB_TYPES")
