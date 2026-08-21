"""
HTTP client for the Insight timeseries catalog API.

Used *only* when a writer's InfluxDB sink is active — see the sink-conditional
rule in energydesk-insight's plans/08_timeseries_api.md section 11. Writers
that only write to the Energydesk REST API or Postgres sinks never import or
call this module in a way that requires it to be configured.

Insight exposes two identically-shaped catalog route trees —
/api/timeseries/assetdata/... and /api/timeseries/marketdata/... — each
fixed to its own catalog database; there is no per-request routing between
them (see energydesk-insight's insight/api/timeseries_catalog.py). A single
`marketdata` flag on every function here does double duty: it selects the
URL path (assetdata/ vs marketdata/) AND, since a deployment serving one
customer's data doesn't necessarily also serve the shared market-data
catalog, which Insight deployment to call — POD_INSIGHTMARKETDATA_URL when
set, falling back to POD_INSIGHT_URL otherwise (the common case where
they're the same instance, e.g. local dev, or a combined deployment that
has both DB_ASSETDATA_CATALOG and DB_MARKETDATA_CATALOG configured).

Authentication follows SERVICE-AUTH.md (energydesk-ai-context): services
are reached via POD_*_URL env vars and authenticate service-to-service with
the shared API_INTERNAL_POD_TOKEN. Catalog registration only ever happens
from writers / background jobs — the sink-conditional rule guarantees there
is no user context — so the pod token is the correct primary credential
here, not a fallback. (Contrast with user-initiated paths such as loading
contracts from the appserver, where the user's own bearer token must be
forwarded end-to-end.)

The pre-SERVICE-AUTH env vars (INSIGHT_MARKETDATA_API_URL/_TOKEN and
INSIGHT_API_URL/_TOKEN) are still honoured as deprecated fallbacks, with a
warning logged, until all deployments have migrated.

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
    """Raised when the relevant POD_*_URL / API_INTERNAL_POD_TOKEN are not set at call time."""


class CatalogApiError(RuntimeError):
    """Raised on a non-2xx response from the catalog API (other than a handled 409)."""


def _config(marketdata: bool) -> tuple[str, str]:
    # SERVICE-AUTH.md convention: POD_*_URL for service addresses,
    # API_INTERNAL_POD_TOKEN as the shared service-to-service credential.
    if marketdata:
        url = os.getenv("POD_INSIGHTMARKETDATA_URL", "") or os.getenv("POD_INSIGHT_URL", "")
    else:
        url = os.getenv("POD_INSIGHT_URL", "")
    token = os.getenv("API_INTERNAL_POD_TOKEN", "")

    # ── Deprecated fallbacks (pre-SERVICE-AUTH naming) ────────────────────
    # Remove once all deployments have migrated to POD_*_URL /
    # API_INTERNAL_POD_TOKEN in GitOps.
    if not url:
        if marketdata:
            legacy_url = os.getenv("INSIGHT_MARKETDATA_API_URL", "") or os.getenv("INSIGHT_API_URL", "")
        else:
            legacy_url = os.getenv("INSIGHT_API_URL", "")
        if legacy_url:
            logger.warning(
                "Timeseries catalog: using deprecated INSIGHT_*_API_URL env var — "
                "migrate this deployment to POD_INSIGHTMARKETDATA_URL / POD_INSIGHT_URL (see SERVICE-AUTH.md)."
            )
            url = legacy_url
    if not token:
        if marketdata:
            legacy_token = os.getenv("INSIGHT_MARKETDATA_API_TOKEN", "") or os.getenv("INSIGHT_API_TOKEN", "")
        else:
            legacy_token = os.getenv("INSIGHT_API_TOKEN", "")
        if legacy_token:
            logger.warning(
                "Timeseries catalog: using deprecated INSIGHT_*_API_TOKEN env var — "
                "migrate this deployment to API_INTERNAL_POD_TOKEN (see SERVICE-AUTH.md)."
            )
            token = legacy_token

    if not url or not token:
        var_hint = (
            "POD_INSIGHTMARKETDATA_URL (or POD_INSIGHT_URL) and API_INTERNAL_POD_TOKEN"
            if marketdata
            else "POD_INSIGHT_URL and API_INTERNAL_POD_TOKEN"
        )
        raise CatalogNotConfiguredError(f"{var_hint} must be set to use the timeseries catalog client.")
    return url.rstrip("/"), token


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _catalog_path(path: str, marketdata: bool) -> str:
    """e.g. _catalog_path("/definitions/", True) -> "/api/timeseries/marketdata/definitions/"."""
    segment = "marketdata" if marketdata else "assetdata"
    return f"/api/timeseries/{segment}{path}"


def _post(path: str, payload: dict[str, Any], marketdata: bool) -> dict[str, Any]:
    url, token = _config(marketdata)
    full_path = _catalog_path(path, marketdata)
    resp = requests.post(f"{url}{full_path}", json=payload, headers=_headers(token), timeout=_DEFAULT_TIMEOUT)
    if resp.status_code >= 300 and resp.status_code != 409:
        raise CatalogApiError(f"POST {full_path} -> {resp.status_code}: {resp.text}")
    return resp.json() if resp.status_code < 300 else {}


def _get(path: str, marketdata: bool, params: Optional[dict[str, Any]] = None) -> Any:
    url, token = _config(marketdata)
    full_path = _catalog_path(path, marketdata)
    resp = requests.get(f"{url}{full_path}", params=params, headers=_headers(token), timeout=_DEFAULT_TIMEOUT)
    if resp.status_code >= 300:
        raise CatalogApiError(f"GET {full_path} -> {resp.status_code}: {resp.text}")
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
    asset_type: Optional[str] = None,
    asset_sub_type: Optional[str] = None,
    area: Optional[str] = None,
    default_aggregation: Optional[str] = None,
    metadata_json: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """
    Idempotent — the catalog API returns the existing definition if one
    already matches the identity uniqueness constraint (customer_id,
    timeseries_type, entity_type, entity_id, area, unit, resolution, name).

    `asset_type`/`asset_sub_type`: free-text classification for filtering
    (e.g. "production"/"consumption"/"contracts", "fuels"/"hydro"/"wind") —
    not part of the identity constraint, purely descriptive/filterable.

    `marketdata`: True to target the shared market-data Insight deployment
    (POD_INSIGHTMARKETDATA_URL) instead of this writer's own local instance
    (POD_INSIGHT_URL). See module docstring.
    """
    payload = {
        "customer_id": customer_id,
        "name": name,
        "timeseries_type": timeseries_type,
        "unit": unit,
        "resolution": resolution,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "asset_type": asset_type,
        "asset_sub_type": asset_sub_type,
        "area": area,
        "default_aggregation": default_aggregation,
        "metadata_json": metadata_json,
    }
    return _post("/definitions/", payload, marketdata)


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
    result = _post("/instances/", payload, marketdata)
    if result:
        return result

    logger.info(
        "Instance already exists for definition=%s date=%s status=%s scenario=%s currency=%s — fetching it.",
        definition_id, timeseries_date, status, scenario, currency,
    )
    existing = _get("/instances/", marketdata, params={"definition_id": definition_id})
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
    asset_type: Optional[str] = None,
    asset_sub_type: Optional[str] = None,
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
    (POD_INSIGHTMARKETDATA_URL, falling back to POD_INSIGHT_URL if unset)
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
        asset_type=asset_type,
        asset_sub_type=asset_sub_type,
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
