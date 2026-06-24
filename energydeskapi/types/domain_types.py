from enum import Enum
from typing import List, Tuple


class MetricDomain(str, Enum):
    ETRM  = "etrm"
    INFRA = "infra"
    RPI   = "rpi"   # Raspberry Pi edge platform — IoT workers, influx-sink, VEN server


class EtrmNamespace(str, Enum):
    TRADING    = "trading"
    COMPLIANCE = "compliance"
    RISK       = "risk"
    MARKETDATA = "marketdata"
    DATASYNC   = "datasync"


class InfraNamespace(str, Enum):
    MESSAGING = "messaging"
    COMPUTE   = "compute"
    STORAGE   = "storage"


class RpiNamespace(str, Enum):
    """
    Sub-namespaces within the RPI domain.

    Each namespace maps to one functional layer of the Raspberry Pi edge
    platform.  The values are used as the second segment of a metric key
    (e.g. rpi.worker.telemetry_published_today) and as the scope_namespace
    tag on NormalizedOpsEvent rows in the AIOps database.

    WORKER      — Per-worker-id counters for publish attempts, command
                  handling and heartbeats.  One metric set per worker_id.
                  Source: device workers (simulation, ekoda, victron, ams …)

    SINK        — Per-source-worker counters for messages confirmed written
                  to InfluxDB.  The gap between WORKER and SINK values is
                  the silent-data-loss signal.
                  Source: influx-sink worker

    VENSERVER   — VEN server resource registrations, setpoint lifecycle
                  events and API health.
                  Source: venserver FastAPI application

    EDGE        — RPi host-level health: CPU temperature, memory pressure,
                  k3s/k3d cluster stability, SQLite WAL size.
                  Source: node-exporter / future host-metrics worker
    """
    WORKER    = "worker"     # Device worker publish/command/heartbeat counters
    SINK      = "sink"       # Influx-sink confirmed-write counters
    VENSERVER = "venserver"  # VEN server registration and setpoint events
    EDGE      = "edge"       # RPi host / cluster health metrics


class DashboardRole(str, Enum):
    TRADING_DESK    = "trading_desk"
    RISK_MANAGER    = "risk_manager"
    COMPLIANCE      = "compliance"
    INFRA_OPS       = "infra_ops"
    BSP_OPS         = "bsp_ops"   # Edge / BSP operators — full RPI domain visibility


# Scopes visible to each dashboard role: list of (MetricDomain, namespace) pairs.
DASHBOARD_ROLE_SCOPES: dict = {
    DashboardRole.TRADING_DESK: [
        (MetricDomain.ETRM, EtrmNamespace.TRADING),
        (MetricDomain.ETRM, EtrmNamespace.MARKETDATA),
        (MetricDomain.ETRM, EtrmNamespace.DATASYNC),
        (MetricDomain.INFRA, InfraNamespace.MESSAGING),
    ],
    DashboardRole.RISK_MANAGER: [
        (MetricDomain.ETRM, EtrmNamespace.TRADING),
        (MetricDomain.ETRM, EtrmNamespace.RISK),
        (MetricDomain.ETRM, EtrmNamespace.MARKETDATA),
    ],
    DashboardRole.COMPLIANCE: [
        (MetricDomain.ETRM, EtrmNamespace.COMPLIANCE),
        (MetricDomain.ETRM, EtrmNamespace.TRADING),
    ],
    DashboardRole.INFRA_OPS: [
        (MetricDomain.INFRA, InfraNamespace.MESSAGING),
        (MetricDomain.INFRA, InfraNamespace.COMPUTE),
        (MetricDomain.INFRA, InfraNamespace.STORAGE),
    ],
    DashboardRole.BSP_OPS: [
        (MetricDomain.RPI, RpiNamespace.WORKER),
        (MetricDomain.RPI, RpiNamespace.SINK),
        (MetricDomain.RPI, RpiNamespace.VENSERVER),
        (MetricDomain.RPI, RpiNamespace.EDGE),
        (MetricDomain.INFRA, InfraNamespace.MESSAGING),  # NATS health relevant to BSP operators
    ],
}


def metric_key(domain: MetricDomain, namespace: str | Enum, name: str) -> str:
    """Build a dot-separated metric key: <domain>.<namespace>.<name>"""
    ns = namespace.value if isinstance(namespace, Enum) else namespace
    return f"{domain.value}.{ns}.{name}"


def nats_subject(domain: MetricDomain, namespace: str | Enum, event: str) -> str:
    """Build a NATS subject: ops.event.<domain>.<namespace>.<event>"""
    ns = namespace.value if isinstance(namespace, Enum) else namespace
    return f"ops.event.{domain.value}.{ns}.{event}"
