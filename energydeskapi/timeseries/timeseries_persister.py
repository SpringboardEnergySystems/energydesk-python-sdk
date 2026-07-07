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
        "price_area":  "NO2",          # str,   optional ("" = unknown) — spot market price area (e.g. NO2, DE)
        "bidzone":     "NO2",          # str,   optional ("" = unknown) — TSO balancing zone (e.g. DE-TenneT)
    }

``lat``, ``lon``, ``capacity_mw``, and ``bidzone`` are optional and default
to their zero/empty values when absent.
"""

from __future__ import annotations

import logging
from datetime import timezone
from typing import Optional

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


def _register_catalog_instance(
    *,
    customer_id: str,
    timeseries_date: str,
    forecast_type: str,
    scenario: str,
    resolution: str,
    tags: dict,
    writer,
) -> Optional[str]:
    """
    Best-effort catalog registration — see energydesk-insight's
    plans/08_timeseries_api.md section 11 (the sink-conditional rule). This
    is only ever called from the InfluxDB write path, and a catalog failure
    (unconfigured, unreachable, etc.) must never block the InfluxDB write
    itself — it just means the point goes out without a series_key, falling
    back to tag-scan discovery like before the catalog existed.
    """
    try:
        from energydeskapi.timeseries.catalog_client import get_or_create_definition_and_instance
        from energydeskapi.timeseries.influx_schema import ASSET_FORECAST

        return get_or_create_definition_and_instance(
            customer_id=customer_id,
            name=f"{tags['asset_name']} {forecast_type} forecast",
            timeseries_type="forecast",
            unit="MWh",
            resolution=resolution,
            timeseries_date=timeseries_date,
            influx_bucket=writer.bucket,
            influx_measurement=ASSET_FORECAST,
            # marketdata=False (default) — this writer's bucket
            # (celsio_assetdata et al.) is always this deployment's own local
            # (customer-scoped) Insight instance, per INSIGHT_API_URL.
            entity_type="asset",
            entity_id=str(tags["asset_id"]),
            area=tags.get("price_area") or None,
            scenario=scenario,
            instance_metadata_json={"forecast_type": forecast_type},
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "Catalog registration failed for asset %s (%s, scenario=%s, date=%s) — "
            "writing to InfluxDB without a series_key. Reason: %s",
            tags.get("asset_id"), forecast_type, scenario, timeseries_date, exc,
        )
        return None


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
    price_area: str,
    bidzone: str,
    resolution: str,
    customer_id: Optional[str] = None,
    timeseries_date: Optional[str] = None,
) -> int:
    """
    Shared implementation for production and sales forecast writes.

    When `customer_id` and `timeseries_date` are both given, this registers
    one timeseries catalog instance for the whole call (one publication run)
    and tags every point in it with the resulting series_key — see
    energydeskapi.timeseries.catalog_client and energydesk-insight's
    plans/08_timeseries_api.md. Both are optional and default to None:
    existing callers that don't pass them keep writing exactly as before,
    with no series_key and no catalog dependency.

    `forecast_type` ("production"/"sales") is written as the InfluxDB
    `asset_type` tag — this demo path has no appserver asset_category to
    source it from (unlike celsiodata-service's assetdata_persister.py,
    which sources it from the real asset classification), so the
    caller-provided forecast direction is the best available proxy.
    """
    tags = _base_tags(asset_meta)
    if price_area:
        tags["price_area"] = price_area
    if bidzone:
        tags["bidzone"] = bidzone

    series_key = None
    if customer_id and timeseries_date:
        series_key = _register_catalog_instance(
            customer_id=customer_id,
            timeseries_date=timeseries_date,
            forecast_type=forecast_type,
            scenario=scenario,
            resolution=resolution,
            tags=tags,
            writer=writer,
        )

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
                asset_sub_type=tags["asset_type"],
                owner=tags["owner"],
                asset_type=forecast_type,
                value_mwh=float(val),
                timestamp=ts,
                capacity_mw=tags["capacity_mw"],
                lat=tags["lat"],
                lon=tags["lon"],
                price_area=tags["price_area"],
                bidzone=tags["bidzone"],
                scenario=scenario,
                resolution=resolution,
                series_key=series_key,
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
    price_area: str = "",
    bidzone: str = "",
    resolution: str = "month",
    customer_id: Optional[str] = None,
    timeseries_date: Optional[str] = None,
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
    price_area:
        Optional spot market price area override (e.g. ``"NO2"``, ``"DE"``).
        When non-empty, overrides the value in ``asset_meta``.
    bidzone:
        Optional bidding-zone override.  When non-empty, overrides the
        value in ``asset_meta``.
    resolution:
        Duration of each data point (default ``"month"``).
    customer_id:
        When given together with ``timeseries_date``, registers this call as
        one timeseries catalog instance (energydesk-insight's
        plans/08_timeseries_api.md) and tags every point with the resulting
        series_key. Omit both (the default) to write exactly as before, with
        no catalog dependency. Catalog registration is best-effort — failures
        are logged and never block the InfluxDB write.
    timeseries_date:
        Publication/run date for the catalog instance, ``"YYYY-MM-DD"``. See
        ``customer_id``.

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
        price_area=price_area,
        bidzone=bidzone,
        resolution=resolution,
        customer_id=customer_id,
        timeseries_date=timeseries_date,
    )


def write_sales_forecast_to_influx(
    monthly_rows: list[dict],
    asset_meta: dict,
    writer,
    scenario: str = "median",
    price_area: str = "",
    bidzone: str = "",
    resolution: str = "month",
    customer_id: Optional[str] = None,
    timeseries_date: Optional[str] = None,
) -> int:
    """Write monthly sales forecast rows to InfluxDB.

    Identical to ``write_production_forecast_to_influx`` except the value
    key is ``"forecast_sales_mwh"`` and ``forecast_type`` is ``"sales"``.
    See that function's docstring for ``customer_id`` / ``timeseries_date``
    (optional catalog registration).

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
    price_area:
        Optional spot market price area override (e.g. ``"NO2"``, ``"DE"``).
        When non-empty, overrides the value in ``asset_meta``.
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
        price_area=price_area,
        bidzone=bidzone,
        resolution=resolution,
        customer_id=customer_id,
        timeseries_date=timeseries_date,
    )
