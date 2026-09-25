"""
API wrappers for the margin record (plans/customer_account_model.md,
"Margin model" section - step 3, not yet built in the appserver). Paths are
the ones the plan's REST table specifies; these will 404 until step 3
ships. Included now so the clearing-service reader (step 4) can be written
against a stable client surface from day one.

Same static-method + ApiConnection style as agreements_api.py /
energydeskapi/contracts/contracts_api.py. Batch POST bodies are plain
lists of the corresponding *Write pydantic type from
energydeskapi.types.margining, serialized with `.model_dump(mode="json")`
by the caller before passing in (same convention as
ContractsApi.bulk_insert_contracts's `json_list`) - these wrappers accept
plain dicts/lists so callers aren't forced through pydantic if they
already have a dict.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from energydeskapi.sdk.api_connection import ApiConnection

logger = logging.getLogger(__name__)


class MarginingApi:
    @staticmethod
    def get_margin_accounts(
        api_connection: ApiConnection, kind: Optional[str] = None, embedded: bool = False,
        parameters: Optional[dict] = None,
    ) -> Any:
        """List margin accounts, optionally filtered to one MarginAccountKindEnum code."""
        params = dict(parameters or {})
        if kind is not None:
            params["kind"] = kind
        suburl = "/api/agreements/margin-accounts/embedded/" if embedded else "/api/agreements/margin-accounts/"
        logger.info("Listing margin accounts (kind=%s)", kind)
        return api_connection.exec_get_url(suburl, params)

    @staticmethod
    def get_margin_account(api_connection: ApiConnection, margin_account_pk: int) -> Any:
        logger.info("Loading margin account %s", margin_account_pk)
        return api_connection.exec_get_url(f"/api/agreements/margin-accounts/{margin_account_pk}/")

    @staticmethod
    def upsert_margin_account(api_connection: ApiConnection, payload: dict, margin_account_pk: Optional[int] = None):
        """Creates/updates a MarginAccount. PATCHes when margin_account_pk
        is given, otherwise POSTs a new row (same upsert shape as
        CounterPartsApi.upsert_counterpart_allowances)."""
        if margin_account_pk:
            logger.info("Updating margin account %s", margin_account_pk)
            return api_connection.exec_patch_url(f"/api/agreements/margin-accounts/{margin_account_pk}/", payload)
        logger.info("Creating margin account")
        return api_connection.exec_post_url("/api/agreements/margin-accounts/", payload)

    @staticmethod
    def get_margin_account_url(api_connection: ApiConnection, margin_account_pk: int) -> str:
        return api_connection.get_base_url() + f"/api/agreements/margin-accounts/{margin_account_pk}/"

    @staticmethod
    def get_margin_account_collateral(api_connection: ApiConnection, margin_account_pk: int) -> Any:
        logger.info("Loading collateral for margin account %s", margin_account_pk)
        return api_connection.exec_get_url(f"/api/agreements/margin-accounts/{margin_account_pk}/collateral/")

    @staticmethod
    def get_collateral_assets(api_connection: ApiConnection, parameters: Optional[dict] = None) -> Any:
        """List collateral assets, filtered by any query params the
        viewset supports (account, direction, is_active-style
        validity-at-date, linked_asset, ...)."""
        params = dict(parameters or {})
        logger.info("Listing collateral assets (filters=%s)", params)
        return api_connection.exec_get_url("/api/agreements/collateral-assets/", params)

    @staticmethod
    def get_collateral_asset(api_connection: ApiConnection, collateral_asset_pk: int) -> Any:
        logger.info("Loading collateral asset %s", collateral_asset_pk)
        return api_connection.exec_get_url(f"/api/agreements/collateral-assets/{collateral_asset_pk}/")

    @staticmethod
    def upsert_collateral_asset(
        api_connection: ApiConnection, payload: dict, collateral_asset_pk: Optional[int] = None,
    ):
        """Creates/updates a CollateralAsset. Body is an
        energydeskapi.types.margining.CollateralAssetWrite-shaped dict
        (direction, amortization_type, amortization_schedule,
        linked_asset, notional_percent are all optional)."""
        if collateral_asset_pk:
            logger.info("Updating collateral asset %s", collateral_asset_pk)
            return api_connection.exec_patch_url(f"/api/agreements/collateral-assets/{collateral_asset_pk}/", payload)
        logger.info("Creating collateral asset")
        return api_connection.exec_post_url("/api/agreements/collateral-assets/", payload)

    @staticmethod
    def get_collateral_asset_url(api_connection: ApiConnection, collateral_asset_pk: int) -> str:
        return api_connection.get_base_url() + f"/api/agreements/collateral-assets/{collateral_asset_pk}/"

    @staticmethod
    def get_margin_requirements(api_connection: ApiConnection, parameters: Optional[dict] = None) -> Any:
        """List margin requirements, filtered by any query params the
        viewset supports (account, as_of, component, source, ...)."""
        params = dict(parameters or {})
        logger.info("Listing margin requirements (filters=%s)", params)
        return api_connection.exec_get_url("/api/agreements/margin-requirements/", params)

    @staticmethod
    def get_margin_requirement(api_connection: ApiConnection, margin_requirement_pk: int) -> Any:
        logger.info("Loading margin requirement %s", margin_requirement_pk)
        return api_connection.exec_get_url(f"/api/agreements/margin-requirements/{margin_requirement_pk}/")

    @staticmethod
    def upsert_margin_requirement(
        api_connection: ApiConnection, payload: dict, margin_requirement_pk: Optional[int] = None,
    ):
        """Creates/updates a single MarginRequirement. For batch
        write-back of many rows in one call, use
        post_margin_requirements instead."""
        if margin_requirement_pk:
            logger.info("Updating margin requirement %s", margin_requirement_pk)
            return api_connection.exec_patch_url(
                f"/api/agreements/margin-requirements/{margin_requirement_pk}/", payload)
        logger.info("Creating margin requirement")
        return api_connection.exec_post_url("/api/agreements/margin-requirements/", payload)

    @staticmethod
    def get_margin_requirement_url(api_connection: ApiConnection, margin_requirement_pk: int) -> str:
        return api_connection.get_base_url() + f"/api/agreements/margin-requirements/{margin_requirement_pk}/"

    @staticmethod
    def post_margin_requirements(api_connection: ApiConnection, requirements: list[dict]):
        """Batch write-back of MarginRequirement rows. Body is a plain list
        of energydeskapi.types.margining.MarginRequirementWrite-shaped
        dicts (batch bodies are lists, not a wrapper object - same
        convention as ContractsApi.bulk_insert_contracts)."""
        logger.info("Posting %d margin requirement(s)", len(requirements))
        return api_connection.exec_post_url("/api/agreements/margin-requirements/", requirements)

    @staticmethod
    def post_margin_calls(api_connection: ApiConnection, calls: list[dict]):
        """Batch write-back of MarginCall rows. Body is a plain list of
        energydeskapi.types.margining.MarginCallWrite-shaped dicts."""
        logger.info("Posting %d margin call(s)", len(calls))
        return api_connection.exec_post_url("/api/agreements/margin-calls/", calls)

    @staticmethod
    def post_collateral_movements(api_connection: ApiConnection, movements: list[dict]):
        """Batch write-back of CollateralMovement rows. Body is a plain
        list of energydeskapi.types.margining.CollateralMovementWrite-shaped
        dicts."""
        logger.info("Posting %d collateral movement(s)", len(movements))
        return api_connection.exec_post_url("/api/agreements/collateral-movements/", movements)
