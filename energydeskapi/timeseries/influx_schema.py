"""
InfluxDB line-protocol schema definitions for all measurements.

Measurements
------------
production_forecast
    Tags  : source, currency_pair, base_currency, quote_currency, resolution
    Fields: rate (float)

Design decisions
----------------
* All tag values are strings.
* All field values are **explicitly cast to float** — InfluxDB rejects writes
  when the same field has been stored as int in one line and float in another.
  Every factory here calls ``float()`` unconditionally before building the
  ``Point``, so mixed-type errors are impossible at the write layer.
* Currency information is carried exclusively as a ``currency`` tag.
  There are **no** per-currency field aliases (e.g. ``price_eur``).
  Use ``|> filter(fn: (r) => r.currency == "EUR")`` in Flux instead.
* ``reserve_type`` uses singular form for consistency with all other tag names.
  (Legacy writes used the plural ``reserves_type`` — re-index or alias in Flux
  if you need to join old and new data.)
* ``resolution`` describes the duration of each data point starting at
  ``timestamp``, e.g. ``"15min"`` for ENTSOE quarter-hourly data,
  ``"hour"`` for hourly spot prices, ``"day"`` for daily cross-rates.
  Callers may override the default by passing the ``resolution`` keyword.
"""

from __future__ import annotations

from influxdb_client import Point

# ── Measurement names ─────────────────────────────────────────────────────────

PRODUCTION_FORECAST = "production_forecast"
SALES_FORECAST = "sales_forecast"


# ── Point factories ───────────────────────────────────────────────────────────


def production_forecast_point(
    *,
    currency_pair: str,
    rate: float,
    timestamp,
    source: str = "norges_bank",
    resolution: str = "day",
) -> Point:
    """Return an InfluxDB ``Point`` for the ``cross_rates`` measurement.

    Parameters
    ----------
    currency_pair:
        Six-character ISO string, e.g. ``"EURNOK"``.
    rate:
        Exchange rate (base → quote), stored as float.
    timestamp:
        Any value accepted by ``influxdb_client.Point.time()``.
    source:
        Data source tag (default ``"norges_bank"``).
    resolution:
        Duration of each data point, e.g. ``"day"`` (default).
    """
    return (
        Point(PRODUCTION_FORECAST)
        .tag("source", source)
        .tag("currency_pair", currency_pair)
        .tag("base_currency", currency_pair[:3])
        .tag("quote_currency", currency_pair[3:])
        .tag("resolution", resolution)
        .field("rate", float(rate))
        .time(timestamp)
    )


def sales_forecast_point(
    *,
    area: str,
    price: float,
    currency: str,
    timestamp,
    resolution: str = "hour",
    status: str = "official",
) -> Point:
    """Return an InfluxDB ``Point`` for the ``spot_prices`` measurement.

    Parameters
    ----------
    area:
        Bidding-zone code, e.g. ``"NO1"``.
    price:
        Spot price, stored as float.
    currency:
        ISO currency code, e.g. ``"EUR"`` or ``"NOK"``.
    timestamp:
        Any value accepted by ``influxdb_client.Point.time()``.
    resolution:
        Duration of each data point, e.g. ``"hour"`` (default).
    status:
        ``"official"`` (from EnergyDesk API / auction results) or
        ``"preliminary"`` (from web-scraped Nord Pool data).
    """
    return (
        Point(SALES_FORECAST)
        .tag("area", area)
        .tag("currency", currency)
        .tag("resolution", resolution)
        .tag("status", status)
        .field("price", float(price))
        .time(timestamp)
    )

