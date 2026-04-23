from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from energydeskapi.collector.protocols import ApiSink, InfluxSink, PostgresSink


@dataclass(frozen=True)
class SinkBundle:
    """Carries optional domain-data sinks into job handlers.

    The runner creates one ``SinkBundle`` per process and forwards it as the
    second argument to every handler call.  Fields that are ``None`` mean the
    sink is not available in this deployment.

    All three fields are typed against thin Protocols so handlers get IDE
    autocomplete without the SDK importing ``influxdb-client``, ``asyncpg``,
    or ``requests`` directly.

    Typical factory setups
    ----------------------
    *Collector service* (Influx + Postgres)::

        sinks = SinkBundle(influx=influx_store, postgres=pg_store)

    *Syncer* (API only)::

        api_conn = ApiConnection(url)
        api_conn.set_token(tok, "Token")
        sinks = SinkBundle(api=api_conn)

    *Hybrid* (all three)::

        sinks = SinkBundle(influx=influx_store, postgres=pg_store, api=api_conn)
    """

    influx: "InfluxSink | None" = None
    # asyncpg Pool / PgStore — for direct domain-data DB writes from handlers.
    postgres: "PostgresSink | None" = None
    # ApiConnection / ApiTempConnection — for writing via the Energydesk REST API.
    api: "ApiSink | None" = None
