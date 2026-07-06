"""
HTTP client for the Insight timeseries catalog API.

Used *only* when a writer's InfluxDB sink is active — see the sink-conditional
rule in energydesk-insight's plans/08_timeseries_api.md section 11. Writers
that only write to the Energydesk REST API or Postgres sinks never import or
call this module in a way that requires it to be configured.

Each deployed Insight instance is scoped to exactly one catalog database —
there is no namespace/tenant parameter on the API. A writer that needs the
shared market-data catalog rather than its own local (customer-scoped)
catalog talks to a *different* Insight deployment, selected via
INSIGHT_MARKETDATA_API_URL / INSIGHT_MARKETDATA_API_TOKEN rather than by
passing anything in the request. Pass `marketdata=True` to target that
deployment; it falls back to INSIGHT_API_URL/INSIGHT_API_TOKEN when the
marketdata-specific vars aren't set (the common case where they're the same
instance, e.g. local dev).

Construction is lazy: importing this module never touches the network or
raises, even when the relevant env vars are unset. They are only read (and
only raise, via CatalogNotConfiguredError) when get_or_create_definition() /
register_instance() are actually called. This means a worker that imports
the SDK but runs with sinks.influx=None never fails due to missing catalog
config.
"""
from __future__ import annotations

import logging
import os
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)

_DEFAULT_TIMEOUT = 10


class CatalogNotConfiguredError(RuntimeError):
    """Raised when the relevant INSIGHT_*_API_URL / INSIGHT_*_API_TOKEN are not set at call time."""


class CatalogApiError(RuntimeError):
    """Raised on a non-2xx response from the catalog API (other than a handled 409)."""


def _config(marketdata: bool) -> tuple[str, str]:
    if marketdata:
        url = os.getenv("INSIGHT_MARKETDATA_API_URL", "") or os.getenv("INSIGHT_API_URL", "")
        token = os.getenv("INSIGHT_MARKETDATA_API_TOKEN", "") or os.getenv("INSIGHT_API_TOKEN", "")
    else:
        url = os.getenv("INSIGHT_API_URL", "")
        token = os.getenv("INSIGHT_API_TOKEN", "")
    if not url or not token:
        var_hint = "INSIGHT_MARKETDATA_API_URL/_TOKEN (or INSIGHT_API_URL/_TOKEN)" if marketdata else "INSIGHT_API_URL/INSIGHT_API_TOKEN"
        raise CatalogNotConfiguredError(f"{var_hint} must be set to use the timeseries catalog client.")
    return url.rstrip("/"), token


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _post(path: str, payload: dict[str, Any], marketdata: bool) -> dict[str, Any]:
    url, token = _config(marketdata)
    resp = requests.post(f"{url}{path}", json=payload, headers=_headers(token), timeout=_DEFAULT_TIMEOUT)
    if resp.status_code >= 300 and resp.status_code != 409:
        raise CatalogApiError(f"POST {path} -> {resp.status_code}: {resp.text}")
    return resp.json() if resp.status_code < 300 else {}


def _get(path: str, marketdata: bool, params: Optional[dict[str, Any]] = None) -> Any:
    url, token = _config(marketdata)
    resp = requests.get(f"{url}{path}", params=params, headers=_headers(token), timeout=_DEFAULT_TIMEOUT)
    if resp.status_code >= 300:
        raise CatalogApiError(f"GET {path} -> {resp.status_code}: {resp.text}")
    return resp.json()


def get_or_create_definition(
    *,
    customer_id: str,
    name: str,
    timeseries_type: str,
    unit: str,
    resolution: str,
    marketdata: bool = False,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    area: Optional[str] = None,
    default_aggregation: Optional[str] = None,
    metadata_json: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """
    Idempotent — the catalog API returns the existing definition if one
    already matches the identity uniqueness constraint (customer_id,
    timeseries_type, entity_type, entity_id, area, unit, resolution, name).

    `marketdata`: True to target the shared market-data Insight deployment
    (INSIGHT_MARKETDATA_API_URL) instead of this writer's own local instance
    (INSIGHT_API_URL). See module docstring.
    """
    payload = {
        "customer_id": customer_id,
        "name": name,
        "timeseries_type": timeseries_type,
        "unit": unit,
        "resolution": resolution,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "area": area,
        "default_aggregation": default_aggregation,
        "metadata_json": metadata_json,
    }
    return _post("/api/timeseries/definitions/", payload, marketdata)


def register_instance(
    *,
    definition_id: str,
    timeseries_date: str,
    influx_bucket: str,
    influx_measurement: str,
    marketdata: bool = False,
    status: str = "official",
    scenario: Optional[str] = None,
    currency: Optional[str] = None,
    metadata_json: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """
    Register one publication run. Returns the created instance (with its
    `id` — the series_key to write to InfluxDB). If an instance already
    exists for this (definition_id, timeseries_date, status, scenario,
    currency), the catalog API returns 409 — this falls back to fetching
    the existing instance rather than erroring, so re-running the same
    publication is idempotent.

    `marketdata`: see get_or_create_definition. Must match whatever value was
    used to create `definition_id` — mismatching would target a different
    Insight deployment than the one the definition was registered against.
    """
    payload = {
        "definition_id": definition_id,
        "timeseries_date": timeseries_date,
        "status": status,
        "scenario": scenario,
        "currency": currency,
        "influx_bucket": influx_bucket,
        "influx_measurement": influx_measurement,
        "metadata_json": metadata_json,
    }
    result = _post("/api/timeseries/instances/", payload, marketdata)
    if result:
        return result

    logger.info(
        "Instance already exists for definition=%s date=%s status=%s scenario=%s currency=%s — fetching it.",
        definition_id, timeseries_date, status, scenario, currency,
    )
    existing = _get("/api/timeseries/instances/", marketdata, params={"definition_id": definition_id})
    for inst in existing:
        if (
            inst.get("timeseries_date") == timeseries_date
            and inst.get("status") == status
            and inst.get("scenario") == scenario
            and inst.get("currency") == currency
        ):
            return inst
    raise CatalogApiError(
        f"Instance registration returned 409 but no matching existing instance was found "
        f"for definition={definition_id} date={timeseries_date} status={status} scenario={scenario} currency={currency}"
    )


def get_or_create_definition_and_instance(
    *,
    customer_id: str,
    name: str,
    timeseries_type: str,
    unit: str,
    resolution: str,
    timeseries_date: str,
    influx_bucket: str,
    influx_measurement: str,
    marketdata: bool = False,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    area: Optional[str] = None,
    scenario: Optional[str] = None,
    currency: Optional[str] = None,
    status: str = "official",
    default_aggregation: Optional[str] = None,
    definition_metadata_json: Optional[dict[str, Any]] = None,
    instance_metadata_json: Optional[dict[str, Any]] = None,
) -> str:
    """
    Convenience wrapper for the common writer flow: resolve the definition,
    then register (or fetch) the instance, and return the series_key
    (instance id, as a string) to tag InfluxDB points with.

    `marketdata=True` targets the shared market-data Insight deployment
    (INSIGHT_MARKETDATA_API_URL, falling back to INSIGHT_API_URL if unset)
    instead of this writer's own local instance — e.g. a forward-curves
    worker needs the shared catalog even when deployed inside a customer's
    namespace. Both the definition and instance calls use the same value so
    they always land in the same catalog database.
    """
    definition = get_or_create_definition(
        customer_id=customer_id,
        name=name,
        timeseries_type=timeseries_type,
        unit=unit,
        resolution=resolution,
        marketdata=marketdata,
        entity_type=entity_type,
        entity_id=entity_id,
        area=area,
        default_aggregation=default_aggregation,
        metadata_json=definition_metadata_json,
    )
    instance = register_instance(
        definition_id=definition["id"],
        timeseries_date=timeseries_date,
        influx_bucket=influx_bucket,
        influx_measurement=influx_measurement,
        marketdata=marketdata,
        status=status,
        scenario=scenario,
        currency=currency,
        metadata_json=instance_metadata_json,
    )
    return str(instance["id"])
