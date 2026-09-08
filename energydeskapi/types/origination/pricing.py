"""
Typed wrapper for the `pricing` JSON blob on DealVersion.

See energydesk/apps/origination/README.md ("pricing JSON"). Written by
`services.price_version()` (currently a stub payload conforming to this same
shape - see README follow-up 2). Never exposed to the counterpart; internal
only. The Deal Builder's Key Metrics / Structure Comparison / Expected
Revenue Distribution panels read only from this payload, so any new column
shown there must be added here too.

`shape_risk` is LOW | MEDIUM | HIGH; `var_95` is in currency millions over
the delivery period (same convention as RiskDesk).
"""
from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, ConfigDict


class Decomposition(BaseModel):
    model_config = ConfigDict(extra="allow")

    forward_value: float
    shape_adj: float
    volume_risk_adj: float
    imbalance_cost: float
    goo_value: float
    margin: float
    fair_value: float
    offer_price: float


class Scenario(BaseModel):
    model_config = ConfigDict(extra="allow")

    volume_mwh: float
    revenue: float


class MerchantBaseline(BaseModel):
    model_config = ConfigDict(extra="allow")

    expected_revenue: float
    p10_revenue: float
    p90_revenue: float
    residual_merchant_pct: float
    shape_risk: str


class Pricing(BaseModel):
    """Not `extra="forbid"`: pricer_version and scenario keys are expected to
    grow (see README follow-up 2 - real synthetic-pricer/Insight/riskservice
    integration), so unknown top-level fields are preserved rather than
    rejected.
    """
    model_config = ConfigDict(extra="allow")

    currency: str
    priced_at: datetime
    pricer_version: str
    market_data_asof: datetime

    decomposition: Decomposition

    capture_price: float
    goo_value_per_mwh: Optional[float] = None
    imbalance_cost_per_mwh: Optional[float] = None
    residual_merchant_pct: Optional[float] = None
    shape_risk: Optional[str] = None
    var_95: Optional[float] = None

    scenarios: Dict[str, Scenario]
    merchant_baseline: MerchantBaseline
