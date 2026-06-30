"""
domain_types.py — Shared metric domain and namespace taxonomy.

Single source of truth for how operational metrics, events, and dashboard
query_ids are named across all Energydesk services.  Both emitting services
(SDK clients) and consuming services (aiops) import from here so identifiers
never drift.

Hierarchy
---------
  <domain>.<namespace>.<metric_name>

  domain      — top-level functional area (MetricDomain)
  namespace   — sub-area within a domain; for RPI maps 1:1 to worker type
  metric_name — free-form string owned by the emitting service

Examples
--------
  etrm.trading.order_fill_latency_p95
  etrm.datasync.contracts_synced_total
  infra.messaging.consumer_lag
  rpi.ekoda.battery_soc_percent
  rpi.sink.writes_confirmed_total
  backoffice.reconciliation.auto_approval_rate
"""
from __future__ import annotations

from enum import Enum


# ---------------------------------------------------------------------------
# Top-level domains
# ---------------------------------------------------------------------------

class MetricDomain(str, Enum):
    INFRA       = "infra"       # Infrastructure — NATS, compute, storage, k8s
    ETRM        = "etrm"        # Energy Trading & Risk Management
    BACKOFFICE  = "backoffice"  # Back-office — reconciliation, settlement, reporting
    RPI         = "rpi"         # Raspberry Pi edge platform — IoT workers, influx-sink, VEN server


# ---------------------------------------------------------------------------
# Namespaces per domain
# ---------------------------------------------------------------------------

class InfraNamespace(str, Enum):
    PLATFORM  = "platform"   # Kubernetes / container-level metrics (CPU, memory, restarts)
    NETWORK   = "network"    # Network I/O, latency between services
    STORAGE   = "storage"    # Disk I/O, database size, partition health
    MESSAGING = "messaging"  # NATS JetStream consumer lag, publish rate


class EtrmNamespace(str, Enum):
    TRADING    = "trading"    # Order flow, fill rate, exchange connectivity
    COMPLIANCE = "compliance" # Pre-trade compliance checks — pass/fail rates, breach counts
    RISK       = "risk"       # Position limits, VaR utilisation, credit exposure
    MARKETDATA = "marketdata" # Price feed freshness, gap counts, source health
    DATASYNC   = "datasync"   # Portal ↔ exchange data synchronisation counters


class BackofficeNamespace(str, Enum):
    RECONCILIATION = "reconciliation"  # Auto-approval rate, manual queue depth, break counts
    SETTLEMENT     = "settlement"      # Settlement instruction status, failed payments
    REPORTING      = "reporting"       # Regulatory report submission status, latency
    CLEARING       = "clearing"        # Clearing house connectivity, margin call status


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
    GROWATT     — Growatt PV worker (MQTT bridge via grott/ShineMonitor).
                  Source: energydesk-rpi-growattpv

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
    SIM        = "sim"        # Simulation worker
    EKODA      = "ekoda"      # EKODA battery worker
    VICTRON    = "victron"    # Victron battery worker
    AMS        = "ams"        # AMS electricity meter worker
    GROWATT    = "growatt"    # Growatt PV worker

    # ── Cross-cutting ─────────────────────────────────────────────────────
    SINK       = "sink"       # influx-sink confirmed-write counters
    DISPATCHER = "dispatcher" # Regulation-dispatcher lifecycle counters
    VENSERVER  = "venserver"  # VEN server registration and setpoint events
    EDGE       = "edge"       # RPi host / cluster health metrics


# ---------------------------------------------------------------------------
# Dashboard roles
# ---------------------------------------------------------------------------

class DashboardRole(str, Enum):
    INFRA_OPS    = "infra_ops"    # Platform / SRE team — full infra domain
    TRADING_DESK = "trading_desk" # Front office traders — etrm.trading + etrm.marketdata
    RISK_MANAGER = "risk_manager" # Risk — etrm.risk + etrm.trading
    COMPLIANCE   = "compliance"   # Compliance — etrm.compliance + etrm.trading
    BACK_OFFICE  = "back_office"  # Settlement / recon — full backoffice domain
    BSP_OPS      = "bsp_ops"      # Edge / BSP operators — full RPI domain


# Scopes visible to each dashboard role: list of (MetricDomain, namespace | None) pairs.
# None as namespace means "all namespaces in this domain".
DASHBOARD_ROLE_SCOPES: dict[DashboardRole, list[tuple[MetricDomain, str | None]]] = {
    DashboardRole.INFRA_OPS: [
        (MetricDomain.INFRA, None),
    ],
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
    DashboardRole.BACK_OFFICE: [
        (MetricDomain.BACKOFFICE, None),
    ],
    DashboardRole.BSP_OPS: [
        (MetricDomain.RPI, RpiNamespace.SIM),
        (MetricDomain.RPI, RpiNamespace.EKODA),
        (MetricDomain.RPI, RpiNamespace.VICTRON),
        (MetricDomain.RPI, RpiNamespace.AMS),
        (MetricDomain.RPI, RpiNamespace.GROWATT),
        (MetricDomain.RPI, RpiNamespace.SINK),
        (MetricDomain.RPI, RpiNamespace.DISPATCHER),
        (MetricDomain.RPI, RpiNamespace.VENSERVER),
        (MetricDomain.RPI, RpiNamespace.EDGE),
        (MetricDomain.INFRA, InfraNamespace.MESSAGING),
    ],
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def metric_key(domain: MetricDomain, namespace: Enum, metric_name: str) -> str:
    """Compose a canonical metric key: <domain>.<namespace>.<metric_name>.

    Example::

        metric_key(MetricDomain.ETRM, EtrmNamespace.DATASYNC, "contracts_synced_total")
        # -> "etrm.datasync.contracts_synced_total"

        metric_key(MetricDomain.RPI, RpiNamespace.EKODA, "battery_soc_percent")
        # -> "rpi.ekoda.battery_soc_percent"
    """
    if not metric_name or "." in metric_name:
        raise ValueError(
            f"metric_name must be a non-empty string without dots, got: {metric_name!r}"
        )
    return f"{domain.value}.{namespace.value}.{metric_name}"


def metric_key_prefix(domain: MetricDomain, namespace: Enum | None = None) -> str:
    """Return the dot-terminated prefix for filtering metric keys by domain/namespace.

    Example::

        metric_key_prefix(MetricDomain.ETRM)
        # -> "etrm."

        metric_key_prefix(MetricDomain.RPI, RpiNamespace.EKODA)
        # -> "rpi.ekoda."
    """
    if namespace is None:
        return f"{domain.value}."
    return f"{domain.value}.{namespace.value}."


def nats_subject(domain: MetricDomain, namespace: Enum, event_type: str) -> str:
    """Compose a NATS subject: ops.event.<domain>.<namespace>.<event_type>.

    Example::

        nats_subject(MetricDomain.RPI, RpiNamespace.VENSERVER, "registration.ok")
        # -> "ops.event.rpi.venserver.registration.ok"
    """
    return f"ops.event.{domain.value}.{namespace.value}.{event_type}"


def dashboard_scope_prefixes(role: DashboardRole) -> list[str]:
    """Return all metric_key prefixes a dashboard role is entitled to see.

    Example::

        dashboard_scope_prefixes(DashboardRole.TRADING_DESK)
        # -> ["etrm.trading.", "etrm.marketdata.", "etrm.datasync.", "infra.messaging."]
    """
    return [
        metric_key_prefix(domain, ns)
        for domain, ns in DASHBOARD_ROLE_SCOPES[role]
    ]
