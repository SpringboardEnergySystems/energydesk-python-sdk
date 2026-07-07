"""
InfluxDB line-protocol schema definitions for asset forecast measurements.

Measurements
------------
asset_forecast
    A single measurement covering both production and consumption/sales
    forecasts. The ``asset_type`` tag distinguishes them so cross-type
    aggregations (e.g. net position = production - sales) can be done with a
    single Flux query using ``pivot()`` on the tag.

Tag design decisions
--------------------
* ``asset_id`` (string form of the Postgres PK) is the stable join key back
  to the appserver database.  Always present.
* ``asset_name``, ``asset_sub_type``, ``owner`` are denormalised here for
  convenience in dashboard label queries.  They may be stale if the asset
  is renamed; treat the ``asset_id`` as authoritative.
* ``lat`` / ``lon`` are NOT stored as raw floats — high-cardinality float
  tags bloat the InfluxDB series index.  Instead they are bucketed into
  1-degree band strings: ``lat_band="58-59N"``, ``lon_band="7-8E"``.
  This supports regional roll-ups in Flux with a simple filter while
  keeping series cardinality bounded.
* ``price_area`` (e.g. ``"NO1"``, ``"NO2"``, ``"DE"``) is the spot-market
  price area — the zone in which a single clearing price is published.
  In Germany there is one price area (``"DE"``); in the Nordics each
  bidding zone typically maps 1:1 to a price area.  This is the primary
  tag for market-price joins and dashboard filtering.  Pass ``""`` when
  unknown.
* ``bidzone`` (e.g. ``"DE-TenneT"``, ``"DE-Amprion"``) is the TSO
  balancing/control zone — distinct from the spot price area.  Germany
  has four bidzones under one price area; the Nordics are mostly 1:1.
  Useful for grid-constraint analysis and congestion modelling.  Pass
  ``""`` when unknown or not relevant.
* ``asset_type``: broad classification of the series, e.g. ``"production"`` |
  ``"consumption"`` | ``"contracts"`` — mirrors the Insight timeseries
  catalog's ``asset_type`` column (sourced from the appserver's
  ``asset_category`` field; see energydesk-insight's
  plans/08_timeseries_api.md). Using one measurement rather than several
  makes net-position queries trivial:
      |> filter(fn: r => r._measurement == "asset_forecast")
      |> pivot(rowKey: ["_time","asset_id"], columnKey: ["asset_type"], valueColumn: "_value")
      |> map(fn: r => ({ r with net_mwh: r.production - r.consumption }))
* ``asset_sub_type``: finer classification within ``asset_type``, e.g.
  ``"hydro"`` | ``"wind"`` | ``"fuels"`` — mirrors the Insight catalog's
  ``asset_sub_type`` column (sourced from the appserver's ``asset_type``
  field — note the appserver's field names are one level removed from ours).
* ``scenario``: ``"median"`` | ``"high"`` | ``"low"`` (P50/P90/P10 or
  equivalent).  Write three points at the same timestamp when all three
  are available; write only ``"median"`` when a single-scenario forecast is
  stored.  This keeps the schema consistent and makes fan-chart queries easy:
      |> filter(fn: r => r.scenario == "median")
* ``resolution``: duration of each data point, e.g. ``"month"``.
  Callers may pass ``"hour"`` or ``"day"`` for higher-frequency forecasts.

Field design decisions
----------------------
* ``value_mwh`` (float) — the forecast energy in MWh for the period starting
  at ``_time`` and lasting ``resolution``.
* ``capacity_mw`` (float) — the rated capacity of the asset in MW, stored as
  a field (not a tag) so Flux can compute capacity factors inline:
      |> map(fn: r => ({ r with cf: r.value_mwh / (r.capacity_mw * 720.0) }))
  It is repeated on every point for simplicity; the value is small and
  compresses well in InfluxDB's column store.
* All field values are explicitly cast to ``float`` before building the
  Point — InfluxDB rejects writes when the same field has been stored as
  int in one line and float in another.
"""

from __future__ import annotations

from influxdb_client import Point

# ── Measurement name ──────────────────────────────────────────────────────────

ASSET_FORECAST = "asset_forecast"


# ── Tag helpers ───────────────────────────────────────────────────────────────

def _lat_band(lat: float) -> str:
    """Bucket a latitude into a 1-degree band string, e.g. 58.46 -> '58-59N'."""
    lo = int(lat)
    return f"{lo}-{lo + 1}N"


def _lon_band(lon: float) -> str:
    """Bucket a longitude into a 1-degree band string, e.g. 7.92 -> '7-8E'."""
    lo = int(lon)
    return f"{lo}-{lo + 1}E"


# ── Point factory ─────────────────────────────────────────────────────────────

def asset_forecast_point(
    *,
    asset_id: int,
    asset_name: str,
    asset_sub_type: str,
    owner: str,
    asset_type: str,
    value_mwh: float,
    timestamp,
    capacity_mw: float = 0.0,
    lat: float = 0.0,
    lon: float = 0.0,
    price_area: str = "",
    bidzone: str = "",
    scenario: str = "median",
    resolution: str = "month",
    series_key: str | None = None,
) -> Point:
    """Return an InfluxDB ``Point`` for the ``asset_forecast`` measurement.

    Parameters
    ----------
    asset_id:
        Integer PK from the appserver Postgres database.  Stored as a string
        tag (InfluxDB tags are always strings).
    asset_name:
        Human-readable asset description, e.g. ``"Iveland kraftverk"``.
    asset_sub_type:
        Finer asset classification, e.g. ``"hydro"`` or ``"wind"``. Mirrors
        the Insight catalog's ``asset_sub_type`` column.
    owner:
        Company name of the asset owner.
    asset_type:
        Broad asset classification, e.g. ``"production"``, ``"consumption"``,
        or ``"contracts"``. Mirrors the Insight catalog's ``asset_type``
        column.
    value_mwh:
        Forecast energy in MWh for the period starting at ``timestamp``.
    timestamp:
        Any value accepted by ``influxdb_client.Point.time()``.  Should be
        UTC start-of-period (e.g. first second of the month for monthly data).
    capacity_mw:
        Rated capacity in MW.  Used for capacity-factor normalisation in Flux.
    lat:
        Latitude of the asset (decimal degrees).  Bucketed into a band tag.
    lon:
        Longitude of the asset (decimal degrees).  Bucketed into a band tag.
    price_area:
        Spot-market price area, e.g. ``"NO1"``, ``"DE"``.  One clearing price
        per area; primary tag for price joins and dashboard filtering.
        Pass ``""`` when unknown.
    bidzone:
        TSO balancing/control zone, e.g. ``"DE-TenneT"``.  Distinct from
        ``price_area``: Germany has four bidzones under one price area; the
        Nordics are mostly 1:1.  Pass ``""`` when unknown or not relevant.
    scenario:
        Forecast scenario: ``"median"``, ``"high"``, or ``"low"``.
    resolution:
        Duration of each data point, e.g. ``"month"`` (default), ``"day"``,
        ``"hour"``.
    series_key:
        UUID of the timeseries catalog instance this point belongs to (see
        energydeskapi.timeseries.catalog_client and energydesk-insight's
        plans/08_timeseries_api.md). Only set when the caller has registered
        with the catalog — omitted (``None``) is a valid, common case for
        writers that don't use the catalog.
    """
    point = (
        Point(ASSET_FORECAST)
        # --- identity tags (always set) ---
        .tag("asset_id", str(asset_id))
        .tag("asset_name", asset_name)
        .tag("asset_sub_type", asset_sub_type)
        .tag("owner", owner)
        # --- classification tags ---
        .tag("asset_type", asset_type)
        .tag("scenario", scenario)
        .tag("resolution", resolution)
        # --- market tags (bounded cardinality) ---
        # price_area = spot market zone (one clearing price); bidzone = TSO balancing zone
        .tag("price_area", price_area)
        .tag("bidzone", bidzone)
        # --- fields ---
        .field("value_mwh", float(value_mwh))
        .field("capacity_mw", float(capacity_mw))
        .time(timestamp)
    )
    # Only add geo band tags when coordinates are meaningful
    if lat != 0.0:
        point = point.tag("lat_band", _lat_band(lat))
    if lon != 0.0:
        point = point.tag("lon_band", _lon_band(lon))
    if series_key:
        point = point.tag("series_key", series_key)
    return point
