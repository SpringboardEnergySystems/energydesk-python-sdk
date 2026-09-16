"""
Pure compute functions for Plan 22 / Plan 17 derivation rules.

Ported from energydesk/apps/assetdata/timeseries/expressions/ (the
appserver's read-time evaluation path), with the defect that motivated the
port fixed: every time-dependent input here is explicit. No function in
this module reads ``datetime.today()`` or any other wall-clock value --
``as_of`` is always a parameter, per Plan 22 D3.

Window/validity selection (``valid_from``/``valid_to``/``config_valid_from``/
``config_valid_to``/``outside_window``) is deliberately NOT handled here --
that is Plan 22 Step D's job (``rule_config.py``, selecting active rules for
a (group, forecast_date) pair before any of these functions are called).
Mixing rule *selection* into rule *math* was the shape of the original
appserver code (``include_period`` called inline inside the calculation
loop) and made D3's bug (today-anchored tenor) harder to see; keeping them
separate here is deliberate, not an oversight.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from finance.options.opcalc import asian_76, black_76

__all__ = [
    "PercentageResult",
    "percentage",
    "MonthlyPercentageResult",
    "monthly_percentage",
    "FixedOffsetResult",
    "fixed_offset",
    "EuropeanOptionResult",
    "european_option",
    "AsianOptionResult",
    "asian_option",
]


def _clamped_delta(delta: float) -> float:
    """NaN -> 0, then clamp to [0, 1] -- matches the appserver's own
    ``np.isnan(delta)`` guard in option_delta_calc.py, ported verbatim."""
    if delta != delta:  # NaN != NaN is the cheapest NaN check without a numpy import
        return 0.0
    return min(max(delta, 0.0), 1.0)


def _intrinsic_call(price: float, strike: float) -> tuple[float, float]:
    """
    Value and delta of a call option at or after expiry: standard option
    payoff mechanics, not a fallback. An option with zero time to expiry is
    worth exactly max(price - strike, 0), and its delta is exactly 0 or 1 in
    the limit -- this is the mathematically correct answer for
    ``days_to_expiry <= 0``, deliberately not smoothed into a continuous
    value near expiry (Plan 22 section 5's "related defects" flagged this as
    a decision point still needing to be made; resolved here as: keep the
    step function, because it is not actually wrong).
    """
    if strike < price:
        return price - strike, 1.0
    return 0.0, 0.0


@dataclass(frozen=True)
class PercentageResult:
    factor: float  # multiplier on gross, e.g. 0.95 for a 5% reduction


def percentage(factor_pct: float) -> PercentageResult:
    """
    A flat percentage adjustment to gross (Plan 17 section 4.2 PERCENTAGE).
    ``factor_pct`` is signed: -5.0 for a 5% reduction, +5.0 for a 5% uplift.
    Caller applies ``derived = gross * result.factor``.
    """
    return PercentageResult(factor=1.0 + (factor_pct / 100.0))


@dataclass(frozen=True)
class MonthlyPercentageResult:
    factor: float
    month: int


def monthly_percentage(delivery_period: date, factor_pct_by_month: dict) -> MonthlyPercentageResult:
    """
    A percentage adjustment that varies by calendar month -- the fourth rule
    type (``MONTHLY_PERC``, ``calc_monthly_percentages.py``) that Plan 17
    section 2 does not list (Plan 22 section 5's "related defects").
    ``factor_pct_by_month`` is keyed 1 (January) through 12 (December).
    Caller applies ``derived = gross * result.factor``.
    """
    month = delivery_period.month
    if month not in factor_pct_by_month:
        raise ValueError(f"No factor_pct configured for month {month}")
    return MonthlyPercentageResult(factor=1.0 + (factor_pct_by_month[month] / 100.0), month=month)


@dataclass(frozen=True)
class FixedOffsetResult:
    offset: float  # constant shift, same unit as gross (MW or MWh, per the rule's `unit` param)


def fixed_offset(offset: float) -> FixedOffsetResult:
    """
    A constant MW/MWh shift (Plan 17 section 4.2 FIXED_OFFSET). Caller
    applies ``derived = gross + result.offset``.
    """
    return FixedOffsetResult(offset=offset)


@dataclass(frozen=True)
class EuropeanOptionResult:
    delta: float               # clamped to [0, 1]
    option_value: float        # Black-76 (or intrinsic) value, same currency/unit as price and strike
    days_to_expiry: int        # delivery_period - as_of, in days; may be <= 0
    rebate_fraction: float     # portion * delta -- what the appserver's read-time path emits today
    residual_fraction: float   # 1 - rebate_fraction -- gross minus the rebate (Plan 22 section 9, resolved 2026-09-16: this is what the hedging benchmark needs as `net`)


def european_option(
    price: float,
    strike: float,
    as_of: date,
    delivery_period: date,
    volatility: float,
    rate: float,
    portion: float,
) -> EuropeanOptionResult:
    """
    European call option delta and value (Black-76), evaluated as of
    ``as_of`` -- never ``datetime.today()`` (Plan 22 D3, the substantive bug
    fix relative to ``option_delta_calc.py``). ``portion`` is a 0-1 fraction
    (already divided by 100 if the config stores it as a percentage).

    Returns both the rebate fraction (of gross) and the residual fraction,
    so the net-semantics decision (Plan 22 section 9) is the caller's choice
    of which field to use, not baked into this function.
    """
    days = (delivery_period - as_of).days
    t = days / 365.0
    if t > 0:
        value, delta, *_rest = black_76("c", price, strike, t, rate, volatility)
    else:
        value, delta = _intrinsic_call(price, strike)
    delta = _clamped_delta(delta)
    rebate_fraction = portion * delta
    return EuropeanOptionResult(
        delta=delta,
        option_value=value,
        days_to_expiry=days,
        rebate_fraction=rebate_fraction,
        residual_fraction=1.0 - rebate_fraction,
    )


@dataclass(frozen=True)
class AsianOptionResult:
    delta: float
    option_value: float
    days_to_expiry: int
    rebate_fraction: float
    residual_fraction: float


def asian_option(
    price: float,
    strike: float,
    as_of: date,
    delivery_period: date,
    volatility: float,
    rate: float,
    portion: float,
    averaging_fraction: float = 0.9,
) -> AsianOptionResult:
    """
    Average-price (Asian) option delta and value, evaluated as of ``as_of``.
    ``averaging_fraction`` is the fraction of the option's life over which
    the price is averaged (``t_a / t``); 0.9 matches the appserver's
    existing ``calc_asian_option.py`` approximation, made an explicit
    parameter here rather than a hardcoded literal. No production rule
    currently uses ASIAN_OPTION (Plan 22 section 4.2: production has one
    EUROPEAN_OPTION per group, no chaining) -- this is ported for parity
    with the appserver's ``resolve_calculator`` but not yet exercised
    against real numbers.
    """
    days = (delivery_period - as_of).days
    t = days / 365.0
    if t > 0:
        t_a = t * averaging_fraction
        value, delta, *_rest = asian_76("c", price, strike, t, t_a, rate, volatility)
    else:
        value, delta = _intrinsic_call(price, strike)
    delta = _clamped_delta(delta)
    rebate_fraction = portion * delta
    return AsianOptionResult(
        delta=delta,
        option_value=value,
        days_to_expiry=days,
        rebate_fraction=rebate_fraction,
        residual_fraction=1.0 - rebate_fraction,
    )
