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

    The second segment of a metric key is the concrete worker type, not a
    generic functional layer.  This matches the NATS subject convention already
    in use (evt.sim.*, evt.ekoda.*, evt.victron.*, …) and makes Grafana
    filtering straightforward — each panel can select a single namespace to
    show exactly one worker type.

    Per-worker-type namespaces
    ──────────────────────────
    SIM         — Simulation worker (synthetic resources, no hardware).
                  Source: workers/simulation-worker
    EKODA       — EKODA battery workers (Modbus, power-based setpoints only).
                  Source: energydesk-rpi-ekodabattery
    VICTRON     — Victron battery workers (Modbus/VE.Bus).
                  Source: energydesk-rpi-victronbattery
    AMS         — AMS electricity meter reader.
                  Source: future energydesk-rpi-ams repo

    Cross-cutting namespaces
    ────────────────────────
    SINK        — influx-sink confirmed-write counters, keyed per source
                  worker_id.  The gap between a worker namespace and SINK is
                  the silent-data-loss signal.
                  Source: workers/influx-sink
    DISPATCHER  — Regulation-dispatcher setpoint lifecycle, watchdog, re-opt.
                  Source: workers/regulation-dispatcher
    VENSERVER   — VEN server resource registrations and API health.
                  Source: venserver FastAPI application
    EDGE        — RPi host-level health: CPU temp, memory, k3s/SQLite.
                  Source: node-exporter / future host-metrics worker
    """
    # ── Per-worker-type ───────────────────────────────────────────────────
    SIM         = "sim"         # Simulation worker
    EKODA       = "ekoda"       # EKODA battery worker
    VICTRON     = "victron"     # Victron battery worker
    AMS         = "ams"         # AMS electricity meter worker

    # ── Cross-cutting ─────────────────────────────────────────────────────
    SINK        = "sink"        # influx-sink confirmed-write counters
    DISPATCHER  = "dispatcher"  # Regulation-dispatcher lifecycle counters
    VENSERVER   = "venserver"   # VEN server registration and setpoint events
    EDGE        = "edge"        # RPi host / cluster health metrics


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
        # All concrete worker types
        (MetricDomain.RPI, RpiNamespace.SIM),
        (MetricDomain.RPI, RpiNamespace.EKODA),
        (MetricDomain.RPI, RpiNamespace.VICTRON),
        (MetricDomain.RPI, RpiNamespace.AMS),
        # Cross-cutting
        (MetricDomain.RPI, RpiNamespace.SINK),
        (MetricDomain.RPI, RpiNamespace.DISPATCHER),
        (MetricDomain.RPI, RpiNamespace.VENSERVER),
        (MetricDomain.RPI, RpiNamespace.EDGE),
        # NATS health relevant to BSP operators
        (MetricDomain.INFRA, InfraNamespace.MESSAGING),
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
