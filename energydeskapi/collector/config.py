from __future__ import annotations

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # General
    tz: str = Field(default="Europe/Oslo", alias="TZ")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # NATS / JetStream
    nats_url: str = Field(default="nats://nats:4222", alias="NATS_URL")
    js_stream_jobs: str = Field(default="INGEST_JOBS", alias="JS_STREAM_JOBS")
    js_stream_events: str = Field(default="INGEST_EVENTS", alias="JS_STREAM_EVENTS")

    subject_jobs: str = Field(default="ingest.jobs.>", alias="SUBJECT_JOBS")
    subject_runs: str = Field(default="ingest.runs.*", alias="SUBJECT_RUNS")
    subject_dlq: str = Field(default="ingest.dlq", alias="SUBJECT_DLQ")

    durable_name: str = Field(default="collector-workers", alias="DURABLE_NAME")
    ack_wait_seconds: int = Field(default=60, alias="ACK_WAIT_SECONDS")
    max_deliver: int = Field(default=10, alias="MAX_DELIVER")
    worker_concurrency: int = Field(default=4, alias="WORKER_CONCURRENCY")

    # Worker selection
    job_types: str = Field(default="", alias="JOB_TYPES")  # comma-separated; empty = all registered

    # Stores
    influx_url: str = Field(default="http://influxdb-influxdb2.energydesk.svc:8086", alias="INFLUX_URL")
    influx_org: str = Field(default="myorg", alias="INFLUX_ORG")
    influx_bucket: str = Field(default="energydesk_common", alias="INFLUX_BUCKET")
    influx_token: str = Field(default="", alias="INFLUX_TOKEN")

    postgres_dsn: str = Field(default="", alias="POSTGRES_DSN")

    # Portal / API
    app_title: str = Field(default="Energydesk Collector", alias="APP_TITLE")
    app_port: int = Field(default=8080, alias="APP_PORT")
    enable_oidc: bool = Field(default=False, alias="ENABLE_OIDC")
    oidc_secret_key: str = Field(default="", alias="OIDC_SECRET_KEY")

settings = Settings()
