from enum import Enum
from typing import List, Tuple


class MetricDomain(str, Enum):
    ETRM  = "etrm"
    INFRA = "infra"


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


class DashboardRole(str, Enum):
    TRADING_DESK    = "trading_desk"
    RISK_MANAGER    = "risk_manager"
    COMPLIANCE      = "compliance"
    INFRA_OPS       = "infra_ops"


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
}


def metric_key(domain: MetricDomain, namespace: str | Enum, name: str) -> str:
    """Build a dot-separated metric key: <domain>.<namespace>.<name>"""
    ns = namespace.value if isinstance(namespace, Enum) else namespace
    return f"{domain.value}.{ns}.{name}"


def nats_subject(domain: MetricDomain, namespace: str | Enum, event: str) -> str:
    """Build a NATS subject: ops.event.<domain>.<namespace>.<event>"""
    ns = namespace.value if isinstance(namespace, Enum) else namespace
    return f"ops.event.{domain.value}.{ns}.{event}"
