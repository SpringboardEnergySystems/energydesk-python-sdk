"""
HTTP client for the Insight timeseries catalog API.

Used *only* when a writer's InfluxDB sink is active — see the sink-conditional
rule in energydesk-insight's plans/08_timeseries_api.md section 11. Writers
that only write to the Energydesk REST API or Postgres sinks never import or
call this module in a way that requires it to be configured.

Construction is lazy: importing this module never touches the network or
raises, even when INSIGHT_API_URL / INSIGHT_API_TOKEN are unset. Those env
vars are only read (and only raise, via CatalogNotConfiguredError) when
get_or_create_definition() / register_instance() are actually called. This
means a worker that imports the SDK but runs with sinks.influx=None never
fails due to missing catalog config.
"""
from __future__ import annotations

import logging
import os
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)

_DEFAULT_TIMEOUT = 10


class CatalogNotConfiguredError(RuntimeError):
    """Raised when INSIGHT_API_URL / INSIGHT_API_TOKEN are not set at call time."""


class CatalogApiError(RuntimeError):
    """Raised on a non-2xx response from the catalog API (other than a handled 409)."""


def _config() -> tuple[str, str]:
    url = os.getenv("INSIGHT_API_URL", "")
    token = os.getenv("INSIGHT_API_TOKEN", "")
    if not url or not token:
        raise CatalogNotConfiguredError(
            "INSIGHT_API_URL and INSIGHT_API_TOKEN must both be set to use the timeseries catalog client."
        )
    return url.rstrip("/"), token


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _post(path: str, payload: dict[str, Any], params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    url, token = _config()
    resp = requests.post(f"{url}{path}", json=payload, params=params, headers=_headers(token), timeout=_DEFAULT_TIMEOUT)
    if resp.status_code >= 300 and resp.status_code != 409:
        raise CatalogApiError(f"POST {path} -> {resp.status_code}: {resp.text}")
    return resp.json() if resp.status_code < 300 else {}


def _get(path: str, params: Optional[dict[str, Any]] = None) -> Any:
    url, token = _config()
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
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    area: Optional[str] = None,
    default_aggregation: Optional[str] = None,
    metadata_json: Optional[dict[str, Any]] = None,
    namespace: Optional[str] = None,
) -> dict[str, Any]:
    """
    Idempotent — the catalog API returns the existing definition if one
    already matches the identity uniqueness constraint (customer_id,
    timeseries_type, entity_type, entity_id, area, unit, resolution, name).
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
    params = {"namespace": namespace} if namespace else None
    return _post("/api/timeseries/definitions/", payload, params=params)


def register_instance(
    *,
    definition_id: str,
    timeseries_date: str,
    influx_bucket: str,
    influx_measurement: str,
    status: str = "official",
    scenario: Optional[str] = None,
    currency: Optional[str] = None,
    metadata_json: Optional[dict[str, Any]] = None,
    namespace: Optional[str] = None,
) -> dict[str, Any]:
    """
    Register one publication run. Returns the created instance (with its
    `id` — the series_key to write to InfluxDB). If an instance already
    exists for this (definition_id, timeseries_date, status, scenario,
    currency), the catalog API returns 409 — this falls back to fetching
    the existing instance rather than erroring, so re-running the same
    publication is idempotent.
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
    params = {"namespace": namespace} if namespace else None
    result = _post("/api/timeseries/instances/", payload, params=params)
    if result:
        return result

    logger.info(
        "Instance already exists for definition=%s date=%s status=%s scenario=%s currency=%s — fetching it.",
        definition_id, timeseries_date, status, scenario, currency,
    )
    existing = _get("/api/timeseries/instances/", params={"definition_id": definition_id, **(params or {})})
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
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    area: Optional[str] = None,
    scenario: Optional[str] = None,
    currency: Optional[str] = None,
    status: str = "official",
    default_aggregation: Optional[str] = None,
    definition_metadata_json: Optional[dict[str, Any]] = None,
    instance_metadata_json: Optional[dict[str, Any]] = None,
    namespace: Optional[str] = None,
) -> str:
    """
    Convenience wrapper for the common writer flow: resolve the definition,
    then register (or fetch) the instance, and return the series_key
    (instance id, as a string) to tag InfluxDB points with.
    """
    definition = get_or_create_definition(
        customer_id=customer_id,
        name=name,
        timeseries_type=timeseries_type,
        unit=unit,
        resolution=resolution,
        entity_type=entity_type,
        entity_id=entity_id,
        area=area,
        default_aggregation=default_aggregation,
        metadata_json=definition_metadata_json,
        namespace=namespace,
    )
    instance = register_instance(
        definition_id=definition["id"],
        timeseries_date=timeseries_date,
        influx_bucket=influx_bucket,
        influx_measurement=influx_measurement,
        status=status,
        scenario=scenario,
        currency=currency,
        metadata_json=instance_metadata_json,
        namespace=namespace,
    )
    return str(instance["id"])