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
    def get_margin_account_collateral(api_connection: ApiConnection, margin_account_pk: int) -> Any:
        logger.info("Loading collateral for margin account %s", margin_account_pk)
        return api_connection.exec_get_url(f"/api/agreements/margin-accounts/{margin_account_pk}/collateral/")

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
