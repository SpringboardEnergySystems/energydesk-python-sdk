"""
InfluxDB line-protocol schema definitions for asset forecast measurements.

Measurements
------------
asset_forecast
    A single measurement covering both production and sales forecasts.
    The ``forecast_type`` tag distinguishes them so cross-type aggregations
    (e.g. net position = production - sales) can be done with a single Flux
    query using ``pivot()`` on the tag.

Tag design decisions
--------------------
* ``asset_id`` (string form of the Postgres PK) is the stable join key back
  to the appserver database.  Always present.
* ``asset_name``, ``asset_type``, ``owner`` are denormalised here for
  convenience in dashboard label queries.  They may be stale if the asset
  is renamed; treat the ``asset_id`` as authoritative.
* ``lat`` / ``lon`` are NOT stored as raw floats — high-cardinality float
  tags bloat the InfluxDB series index.  Instead they are bucketed into
  1-degree band strings: ``lat_band="58-59N"``, ``lon_band="7-8E"``.
  This supports regional roll-ups in Flux with a simple filter while
  keeping series cardinality bounded.
* ``bidzone`` (e.g. ``"NO1"``, ``"NO2"``) enables price-weighted calculations
  when joined against spot-price measurements.  Pass ``""`` when unknown;
  it can be backfilled once grid-area mapping is available.
* ``forecast_type``: ``"production"`` | ``"sales"``.  Using one measurement
  rather than two makes net-position queries trivial:
      |> filter(fn: r => r._measurement == "asset_forecast")
      |> pivot(rowKey: ["_time","asset_id"], columnKey: ["forecast_type"], valueColumn: "_value")
      |> map(fn: r => ({ r with net_mwh: r.production - r.sales }))
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
    asset_type: str,
    owner: str,
    forecast_type: str,
    value_mwh: float,
    timestamp,
    capacity_mw: float = 0.0,
    lat: float = 0.0,
    lon: float = 0.0,
    bidzone: str = "",
    scenario: str = "median",
    resolution: str = "month",
) -> Point:
    """Return an InfluxDB ``Point`` for the ``asset_forecast`` measurement.

    Parameters
    ----------
    asset_id:
        Integer PK from the appserver Postgres database.  Stored as a string
        tag (InfluxDB tags are always strings).
    asset_name:
        Human-readable asset description, e.g. ``"Iveland kraftverk"``.
    asset_type:
        Asset type description, e.g. ``"hydro"`` or ``"wind"``.
    owner:
        Company name of the asset owner.
    forecast_type:
        ``"production"`` or ``"sales"``.
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
    bidzone:
        Elspot/bidding-zone code, e.g. ``"NO1"``.  Pass ``""`` when unknown.
    scenario:
        Forecast scenario: ``"median"``, ``"high"``, or ``"low"``.
    resolution:
        Duration of each data point, e.g. ``"month"`` (default), ``"day"``,
        ``"hour"``.
    """
    point = (
        Point(ASSET_FORECAST)
        # --- identity tags (always set) ---
        .tag("asset_id", str(asset_id))
        .tag("asset_name", asset_name)
        .tag("asset_type", asset_type)
        .tag("owner", owner)
        # --- classification tags ---
        .tag("forecast_type", forecast_type)
        .tag("scenario", scenario)
        .tag("resolution", resolution)
        # --- geo tags (bounded cardinality) ---
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
    return point
