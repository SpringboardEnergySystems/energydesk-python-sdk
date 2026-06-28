"""Write asset forecast timeseries to InfluxDB.

This module provides the high-level write functions called by the demo setup
(and, in production, by any pipeline that computes production or sales
forecasts).  It sits between the schema layer (``influx_schema.py``) and the
caller, handling timestamp parsing, NaN filtering, per-point error isolation,
and logging.

Expected ``monthly_rows`` shape
-------------------------------
Both functions accept a list of dicts with at least these keys::

    [
        {"period": "2026-04", "forecast_production_mwh": 12345.6},
        ...
    ]

For sales forecasts the value key is ``"forecast_sales_mwh"``.
``period`` must be a string in ``YYYY-MM`` format; the function derives the
UTC timestamp from the first instant of that month in the Europe/Oslo
timezone (matching the convention in ``production_loader.py``).

Expected ``asset_meta`` shape
-----------------------------
::

    {
        "pk":          123,            # int  — Postgres PK
        "name":        "Iveland kraftverk",
        "asset_type":  "hydro",        # or "wind", etc.
        "owner":       "Å Energi",
        "lat":         58.46,          # float, optional (0.0 = unknown)
        "lon":         7.92,           # float, optional (0.0 = unknown)
        "capacity_mw": 87.0,           # float, optional (0.0 = unknown)
        "price_area":  "NO2",          # str,   optional ("" = unknown)
        "bidzone":     "NO2",          # str,   optional ("" = unknown)
    }

``lat``, ``lon``, ``capacity_mw``, ``price_area``, and ``bidzone`` are
optional and default to their zero/empty values when absent.
"""

from __future__ import annotations

import logging
from datetime import timezone

import pendulum

from energydeskapi.timeseries.influx_schema import asset_forecast_point

logger = logging.getLogger(__name__)


# ── Internal helpers ──────────────────────────────────────────────────────────

def _period_to_utc(period: str):
    """Convert a 'YYYY-MM' period string to a UTC datetime.

    Uses the Europe/Oslo timezone to align with the timestamps stored in
    the appserver blob (matching ``production_loader.py``).
    """
    year, month = map(int, period.split("-"))
    oslo_dt = pendulum.datetime(year, month, 1, tz="Europe/Oslo")
    return oslo_dt.in_tz("UTC")


def _is_missing(val) -> bool:
    """Return True for None or float NaN."""
    if val is None:
        return True
    try:
        import math
        return math.isnan(float(val))
    except (TypeError, ValueError):
        return False


def _base_tags(asset_meta: dict) -> dict:
    """Extract and normalise the tag fields from an asset_meta dict."""
    return {
        "asset_id":    int(asset_meta.get("pk", 0)),
        "asset_name":  str(asset_meta.get("name", "")),
        "asset_type":  str(asset_meta.get("asset_type", "")),
        "owner":       str(asset_meta.get("owner", "")),
        "lat":         float(asset_meta.get("lat", 0.0)),
        "lon":         float(asset_meta.get("lon", 0.0)),
        "capacity_mw": float(asset_meta.get("capacity_mw", 0.0)),
        "price_area":  str(asset_meta.get("price_area", "")),
        "bidzone":     str(asset_meta.get("bidzone", "")),
    }


def _write_forecast(
    monthly_rows: list[dict],
    asset_meta: dict,
    writer,
    forecast_type: str,
    value_key: str,
    scenario: str,
    bidzone: str,
    resolution: str,
) -> int:
    """Shared implementation for production and sales forecast writes."""
    tags = _base_tags(asset_meta)
    if bidzone:
        tags["bidzone"] = bidzone

    points_written = 0
    for row in monthly_rows:
        try:
            val = row.get(value_key)
            if _is_missing(val):
                continue
            period = row.get("period", "")
            if not period:
                logger.warning(
                    "Skipping row with missing 'period' for asset %s: %s",
                    tags["asset_id"], row,
                )
                continue
            ts = _period_to_utc(period)
            point = asset_forecast_point(
                asset_id=tags["asset_id"],
                asset_name=tags["asset_name"],
                asset_type=tags["asset_type"],
                owner=tags["owner"],
                forecast_type=forecast_type,
                value_mwh=float(val),
                timestamp=ts,
                capacity_mw=tags["capacity_mw"],
                lat=tags["lat"],
                lon=tags["lon"],
                price_area=tags["price_area"],
                bidzone=tags["bidzone"],
                scenario=scenario,
                resolution=resolution,
            )
            writer.write_api.write(bucket=writer.bucket, org=writer.org, record=point)
            points_written += 1
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "Error writing %s forecast point for asset %s, period %s: %s",
                forecast_type,
                tags.get("asset_id"),
                row.get("period"),
                exc,
            )

    logger.info(
        "Wrote %d %s forecast points (scenario=%s) for asset %s (%s) to bucket '%s'.",
        points_written,
        forecast_type,
        scenario,
        tags["asset_id"],
        tags["asset_name"],
        writer.bucket,
    )
    return points_written


# ── Public API ────────────────────────────────────────────────────────────────

def write_production_forecast_to_influx(
    monthly_rows: list[dict],
    asset_meta: dict,
    writer,
    scenario: str = "median",
    bidzone: str = "",
    resolution: str = "month",
) -> int:
    """Write monthly production forecast rows to InfluxDB.

    Parameters
    ----------
    monthly_rows:
        List of dicts, each with ``"period"`` (``"YYYY-MM"``) and
        ``"forecast_production_mwh"`` (float).  Rows where the value is
        ``None`` or ``NaN`` are silently skipped.
    asset_meta:
        Asset metadata dict — see module docstring for the expected shape.
    writer:
        An ``_InfluxWriter`` instance (from ``build_influx_sink()``).
    scenario:
        Forecast scenario tag: ``"median"`` (default), ``"high"``, or
        ``"low"``.
    bidzone:
        Optional bidding-zone override.  When non-empty, overrides the
        value in ``asset_meta``.
    resolution:
        Duration of each data point (default ``"month"``).

    Returns
    -------
    int
        Number of points successfully written.
    """
    return _write_forecast(
        monthly_rows=monthly_rows,
        asset_meta=asset_meta,
        writer=writer,
        forecast_type="production",
        value_key="forecast_production_mwh",
        scenario=scenario,
        bidzone=bidzone,
        resolution=resolution,
    )


def write_sales_forecast_to_influx(
    monthly_rows: list[dict],
    asset_meta: dict,
    writer,
    scenario: str = "median",
    bidzone: str = "",
    resolution: str = "month",
) -> int:
    """Write monthly sales forecast rows to InfluxDB.

    Identical to ``write_production_forecast_to_influx`` except the value
    key is ``"forecast_sales_mwh"`` and ``forecast_type`` is ``"sales"``.

    Parameters
    ----------
    monthly_rows:
        List of dicts, each with ``"period"`` (``"YYYY-MM"``) and
        ``"forecast_sales_mwh"`` (float).
    asset_meta:
        Asset metadata dict — see module docstring for the expected shape.
    writer:
        An ``_InfluxWriter`` instance.
    scenario:
        Forecast scenario tag: ``"median"`` (default), ``"high"``, or
        ``"low"``.
    bidzone:
        Optional bidding-zone override.
    resolution:
        Duration of each data point (default ``"month"``).

    Returns
    -------
    int
        Number of points successfully written.
    """
    return _write_forecast(
        monthly_rows=monthly_rows,
        asset_meta=asset_meta,
        writer=writer,
        forecast_type="sales",
        value_key="forecast_sales_mwh",
        scenario=scenario,
        bidzone=bidzone,
        resolution=resolution,
    )
