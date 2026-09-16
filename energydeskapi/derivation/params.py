"""
Rule-parameter schemas for Plan 22 / Plan 17 derivation rules.

A Pydantic discriminated union on ``rule_type``, matching Plan 17 section 4.2's
``params_json`` shape (with the naming correction Plan 22 section 8 amendment
1 records: ``strike``/``portion_pct`` rather than ``notional``/``rate``, and
``volatility``/``risk_free_rate`` promoted from hardcoded literals to
required fields, Plan 22 D5). This is the schema both Plan 22's phase-0 YAML
(``derivation_rules.yaml``) and Plan 17's ``derived_forecast_rule.params_json``
column validate against -- one schema, two storage locations, per Plan 22
section 7 Step L ("Plan 17 Step 3 imports rule_types rather than
reimplementing it").
"""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Dict, Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator

__all__ = [
    "RuleType",
    "OutsideWindowPolicy",
    "PriceSource",
    "PercentageParams",
    "MonthlyPercentageParams",
    "FixedOffsetParams",
    "EuropeanOptionParams",
    "AsianOptionParams",
    "RuleParams",
    "DerivationRule",
]


class RuleType(str, Enum):
    PERCENTAGE = "PERCENTAGE"
    MONTHLY_PERC = "MONTHLY_PERC"
    FIXED_OFFSET = "FIXED_OFFSET"
    EUROPEAN_OPTION = "EUROPEAN_OPTION"
    ASIAN_OPTION = "ASIAN_OPTION"


class OutsideWindowPolicy(str, Enum):
    """
    What the derived series equals for a delivery period outside a rule's
    validity window (``valid_from``/``valid_to``). Applied uniformly by the
    caller regardless of rule type -- ``derived = gross`` (PASS_THROUGH) or
    ``derived = 0`` (ZERO) -- never baked into rule_types.py's pure math.
    """
    PASS_THROUGH = "pass_through"
    ZERO = "zero"


class PriceSource(BaseModel):
    """Where an option rule's underlying price comes from (Plan 22 D6-equivalent
    for phase 0 -- Plan 17 D6 resolves this via the catalog instead, once it exists)."""
    timeseries_type: Literal["forward_curve"] = "forward_curve"
    area: str
    currency: str
    scenario: Optional[str] = None


def _fraction(value: float) -> float:
    """A config value may be stored as a percentage (5.25) or a fraction
    (0.0525) -- normalise to a fraction, matching option_delta_calc.py's own
    ``if portion >= 1: portion = portion / 100`` convention."""
    return value / 100.0 if abs(value) >= 1 else value


class PercentageParams(BaseModel):
    rule_type: Literal[RuleType.PERCENTAGE] = RuleType.PERCENTAGE
    factor_pct: float
    outside_window: OutsideWindowPolicy = OutsideWindowPolicy.PASS_THROUGH


class MonthlyPercentageParams(BaseModel):
    rule_type: Literal[RuleType.MONTHLY_PERC] = RuleType.MONTHLY_PERC
    factor_pct_by_month: Dict[int, float]  # keys 1 (January) - 12 (December)
    outside_window: OutsideWindowPolicy = OutsideWindowPolicy.PASS_THROUGH

    @field_validator("factor_pct_by_month")
    @classmethod
    def _all_twelve_months(cls, v: Dict[int, float]) -> Dict[int, float]:
        missing = sorted(set(range(1, 13)) - set(v))
        if missing:
            raise ValueError(f"factor_pct_by_month missing month(s): {missing}")
        return v


class FixedOffsetParams(BaseModel):
    rule_type: Literal[RuleType.FIXED_OFFSET] = RuleType.FIXED_OFFSET
    offset: float
    unit: Literal["MW", "MWh"] = "MW"
    outside_window: OutsideWindowPolicy = OutsideWindowPolicy.PASS_THROUGH


class EuropeanOptionParams(BaseModel):
    rule_type: Literal[RuleType.EUROPEAN_OPTION] = RuleType.EUROPEAN_OPTION
    strike: float
    strike_currency: str
    portion_pct: float
    volatility: float
    risk_free_rate: float
    price_source: PriceSource
    outside_window: OutsideWindowPolicy = OutsideWindowPolicy.ZERO

    @property
    def portion(self) -> float:
        """``portion_pct`` normalised to a 0-1 fraction, matching
        ``rule_types.european_option``'s ``portion`` parameter."""
        return _fraction(self.portion_pct)


class AsianOptionParams(BaseModel):
    rule_type: Literal[RuleType.ASIAN_OPTION] = RuleType.ASIAN_OPTION
    strike: float
    strike_currency: str
    portion_pct: float
    volatility: float
    risk_free_rate: float
    averaging_fraction: float = 0.9
    price_source: PriceSource
    outside_window: OutsideWindowPolicy = OutsideWindowPolicy.ZERO

    @property
    def portion(self) -> float:
        return _fraction(self.portion_pct)


RuleParams = Union[
    PercentageParams,
    MonthlyPercentageParams,
    FixedOffsetParams,
    EuropeanOptionParams,
    AsianOptionParams,
]


class DerivationRule(BaseModel):
    """
    One entry in Plan 22's ``derivation_rules.yaml`` (section 4.3), or one row
    of Plan 17's ``derived_forecast_rule`` table (section 4.1) -- same shape,
    per Plan 22 section 7 Step L.
    """
    name: str
    asset_group: str
    valid_from: Optional[date] = None          # delivery periods this rule affects
    valid_to: Optional[date] = None
    config_valid_from: Optional[date] = None   # vintages this parameter set applies to
    config_valid_to: Optional[date] = None
    params: RuleParams = Field(discriminator="rule_type")
