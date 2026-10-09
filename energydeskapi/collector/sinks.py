from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from energydeskapi.collector.nats_client import NatsBus
    from energydeskapi.collector.protocols import ApiSink, InfluxSink, PostgresSink, TimescaleSink


@dataclass(frozen=True)
class SinkBundle:
    """Carries optional domain-data sinks into job handlers.

    The runner creates one ``SinkBundle`` per process and forwards it as the
    second argument to every handler call.  Fields that are ``None`` mean the
    sink is not available in this deployment.

    All fields are typed against thin Protocols or forward references so the
    SDK does not import influxdb-client, asyncpg, requests, or nats-py at
    module level.

    Typical factory setups
    ----------------------
    *Collector service* (Influx and/or Timescale + Postgres)::

        sinks = SinkBundle(influx=influx_store, timescale=ts_store, postgres=pg_store)

    *Syncer* (API + NATS bus for metric events)::

        sinks = SinkBundle(api=api_conn, bus=bus)

    *Hybrid* (all)::

        sinks = SinkBundle(influx=influx_store, postgres=pg_store, api=api_conn, bus=bus)
    """

    influx: "InfluxSink | None" = None
    # Synchronous TimescaleDB writer (series catalog + hypertables) — the
    # successor to ``influx`` for time-series points. Workers that only write
    # Postgres/API are unaffected: the field defaults to None.
    timescale: "TimescaleSink | None" = None
    # asyncpg Pool / PgStore — for direct domain-data DB writes from handlers.
    postgres: "PostgresSink | None" = None
    # ApiConnection / ApiTempConnection — for writing via the Energydesk REST API.
    api: "ApiSink | None" = None
    # NatsBus — for publishing NormalizedOpsEvent from within job handlers.
    # Workers that want to emit metrics after a run should use this rather than
    # creating their own NATS connection.
    bus: "NatsBus | None" = None
