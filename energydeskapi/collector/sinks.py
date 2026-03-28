from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from energydeskapi.collector.protocols import InfluxSink


@dataclass(frozen=True)
class SinkBundle:
    """Carries optional domain-data sinks into job handlers.

    The runner creates one ``SinkBundle`` per process and forwards it as the
    second argument to every handler call.  Fields that are ``None`` mean the
    sink is not available in this deployment (e.g. the syncer has neither
    InfluxDB nor a domain Postgres).

    Typed against the thin ``InfluxSink`` Protocol so handlers get IDE
    autocomplete without the SDK importing ``influxdb-client`` directly.
    """

    influx: "InfluxSink | None" = None
    # Generic slot: pass a PgStore, an asyncpg pool, or any domain-data store.
    postgres: Any | None = None

