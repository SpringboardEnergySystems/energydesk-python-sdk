"""
domain_types.py — Shared metric domain and namespace taxonomy.

This module is the single source of truth for how operational metrics,
events, and dashboard query_ids are named across all Energydesk services.

Both the emitting services (clients using the SDK) and the consuming
aiops service import from here, so the string identifiers never drift.

Hierarchy
---------
  <domain>.<namespace>.<metric_name>

  domain     — top-level functional area (MetricDomain)
  namespace  — sub-area within a domain, often maps 1:1 to a customer
               or a functional slice (MetricNamespace)
  metric_name — free-form string owned by the emitting service

Examples
--------
  infra.platform.cpu_usage_percent
  infra.platform.memory_usage_bytes
  etrm.trading.order_fill_latency_p95
  etrm.compliance.pre_trade_check_pass_rate
  etrm.risk.position_limit_utilisation
  backoffice.reconciliation.auto_approval_rate
  backoffice.settlement.break_count
  iot.telemetry.data_freshness_seconds
  iot.bsp.state_of_charge_percent

Dashboard scoping
-----------------
The MetricNamespace values intentionally align with Kubernetes namespace
conventions used in scope.namespace on NormalizedOpsEvent and MetricSnapshot.
This means dashboard queries can filter metric_snapshots by both
query_id prefix (e.g. "etrm.") AND scope_namespace for per-customer views.

Customer-scoped namespaces follow the pattern  <domain>.<customer_slug>,
e.g. etrm.customer_a  so that a single customer dashboard can be
constructed by filtering on namespace = "customer_a" across any domain.
"""
from __future__ import annotations

from enum import Enum


# ---------------------------------------------------------------------------
# Top-level domains
# ---------------------------------------------------------------------------

class MetricDomain(str, Enum):
    """
    Top-level operational domains.

    Values are used as the first segment of a metric key and as the
    primary grouping for dashboard selection.
    """
    INFRA = "infra"              # Infrastructure — CPU, memory, pod health, k8s platform
    ETRM = "etrm"               # Energy Trading & Risk Management — orders, risk, compliance
    BACKOFFICE = "backoffice"   # Back-office — reconciliation, settlement, approvals
    IOT = "iot"                  # IoT / Edge — Raspberry Pi telemetry, BSP data


# ---------------------------------------------------------------------------
# Namespaces per domain
# ---------------------------------------------------------------------------

class InfraNamespace(str, Enum):
    """
    Sub-namespaces within the INFRA domain.

    In a multi-customer deployment a customer-scoped namespace
    (e.g. "customer_a") can be used in addition to these functional slices.
    """
    PLATFORM = "platform"        # Kubernetes / container-level metrics (CPU, memory, restarts)
    NETWORK = "network"          # Network I/O, latency between services
    STORAGE = "storage"          # Disk I/O, database size, partition health
    MESSAGING = "messaging"      # NATS JetStream consumer lag, publish rate


class EtrmNamespace(str, Enum):
    """
    Sub-namespaces within the ETRM domain.

    Each namespace typically maps to a functional office layer.
    Customer-specific views are achieved by filtering scope_namespace
    on MetricSnapshot / OpsEvent rather than by adding per-customer
    enum members here.
    """
    TRADING = "trading"          # Order flow, fill rate, exchange connectivity, latency
    COMPLIANCE = "compliance"    # Pre-trade compliance checks — pass/fail rates, breach counts
    RISK = "risk"                # Position limits, VaR utilisation, credit exposure
    MARKETDATA = "marketdata"    # Price feed freshness, gap counts, source health


class BackofficeNamespace(str, Enum):
    """
    Sub-namespaces within the BACKOFFICE domain.
    """
    RECONCILIATION = "reconciliation"  # Auto-approval rate, manual queue depth, break counts
    SETTLEMENT = "settlement"          # Settlement instruction status, failed payments
    REPORTING = "reporting"            # Regulatory report submission status, latency
    CLEARING = "clearing"              # Clearing house connectivity, margin call status


class IotNamespace(str, Enum):
    """
    Sub-namespaces within the IOT domain.

    BSP = Battery Storage / Flexibility service provider assets
    managed on Raspberry Pi edge nodes.
    """
    TELEMETRY = "telemetry"      # Raw sensor data freshness, gap detection, transmission rate
    BSP = "bsp"                  # Battery state-of-charge, power output, schedule adherence
    EDGE = "edge"                # RPI system health — CPU temp, memory, connectivity
    COLLECTOR = "collector"      # Collector job scheduling, missed runs, retry counts


# ---------------------------------------------------------------------------
# Composite type for type-safe metric key construction
# ---------------------------------------------------------------------------

# All namespace enums in one union type for function signatures
MetricNamespace = InfraNamespace | EtrmNamespace | BackofficeNamespace | IotNamespace


# ---------------------------------------------------------------------------
# Dashboard definitions — which domains/namespaces each role sees
# ---------------------------------------------------------------------------

class DashboardRole(str, Enum):
    """
    Named dashboard views, one per primary user group.

    Used by the aiops portal to determine which metric query_id prefixes
    and scope_namespace filters to apply when rendering a dashboard page.
    """
    INFRA_OPS = "infra_ops"          # Platform / SRE team — infra domain, all namespaces
    TRADING_DESK = "trading_desk"    # Front office traders — etrm.trading + etrm.marketdata
    MIDDLE_OFFICE = "middle_office"  # Risk / compliance — etrm.compliance + etrm.risk
    BACK_OFFICE = "back_office"      # Settlement / recon — backoffice domain, all namespaces
    BSP_OPS = "bsp_ops"              # Edge / BSP operators — iot domain, all namespaces


# Mapping: which (domain, namespace) prefixes each dashboard role covers
DASHBOARD_ROLE_SCOPES: dict[DashboardRole, list[tuple[MetricDomain, str | None]]] = {
    DashboardRole.INFRA_OPS: [
        (MetricDomain.INFRA, None),          # all infra namespaces
    ],
    DashboardRole.TRADING_DESK: [
        (MetricDomain.ETRM, EtrmNamespace.TRADING),
        (MetricDomain.ETRM, EtrmNamespace.MARKETDATA),
        (MetricDomain.INFRA, InfraNamespace.MESSAGING),  # NATS health relevant to traders
    ],
    DashboardRole.MIDDLE_OFFICE: [
        (MetricDomain.ETRM, EtrmNamespace.COMPLIANCE),
        (MetricDomain.ETRM, EtrmNamespace.RISK),
    ],
    DashboardRole.BACK_OFFICE: [
        (MetricDomain.BACKOFFICE, None),     # all backoffice namespaces
    ],
    DashboardRole.BSP_OPS: [
        (MetricDomain.IOT, None),            # all iot namespaces
        (MetricDomain.INFRA, InfraNamespace.PLATFORM),  # RPI platform metrics
    ],
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def metric_key(domain: MetricDomain, namespace: MetricNamespace, metric_name: str) -> str:
    """
    Compose a canonical metric key from domain, namespace, and metric name.

    This is the value used for MetricSnapshot.query_id in aiops and for
    the query_id field when emitting ops events from client services.

    Example::

        metric_key(MetricDomain.ETRM, EtrmNamespace.TRADING, "order_fill_latency_p95")
        # -> "etrm.trading.order_fill_latency_p95"

        metric_key(MetricDomain.IOT, IotNamespace.BSP, "state_of_charge_percent")
        # -> "iot.bsp.state_of_charge_percent"
    """
    if not metric_name or "." in metric_name:
        raise ValueError(
            f"metric_name must be a non-empty string without dots, got: {metric_name!r}"
        )
    return f"{domain.value}.{namespace.value}.{metric_name}"


def metric_key_prefix(domain: MetricDomain, namespace: MetricNamespace | None = None) -> str:
    """
    Return the prefix used to filter metric_snapshots for a given domain
    (and optionally namespace).

    Used in dashboard query builders::

        # All ETRM metrics
        prefix = metric_key_prefix(MetricDomain.ETRM)
        # -> "etrm."

        # Only trading metrics
        prefix = metric_key_prefix(MetricDomain.ETRM, EtrmNamespace.TRADING)
        # -> "etrm.trading."
    """
    if namespace is None:
        return f"{domain.value}."
    return f"{domain.value}.{namespace.value}."


def nats_subject(domain: MetricDomain, namespace: MetricNamespace, event_type: str) -> str:
    """
    Compose a NATS subject for an operational event following the
    ops.event.<domain>.<namespace>.<event_type> hierarchy.

    Aligns with the ADR-001 subject hierarchy used in energydesk-aiops.

    Example::

        nats_subject(MetricDomain.ETRM, EtrmNamespace.TRADING, "order.ack_timeout")
        # -> "ops.event.etrm.trading.order.ack_timeout"

        nats_subject(MetricDomain.IOT, IotNamespace.TELEMETRY, "freshness.breach")
        # -> "ops.event.iot.telemetry.freshness.breach"
    """
    return f"ops.event.{domain.value}.{namespace.value}.{event_type}"


def dashboard_scope_prefixes(role: DashboardRole) -> list[str]:
    """
    Return all metric_key prefixes a given dashboard role is entitled to see.

    Useful for constructing database WHERE clauses or API filter parameters::

        prefixes = dashboard_scope_prefixes(DashboardRole.TRADING_DESK)
        # -> ["etrm.trading.", "etrm.marketdata.", "infra.messaging."]
    """
    return [
        metric_key_prefix(domain, ns)
        for domain, ns in DASHBOARD_ROLE_SCOPES[role]
    ]
