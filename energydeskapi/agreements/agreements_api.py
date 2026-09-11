"""
API wrappers for energydesk.apps.agreements (plans/customer_account_model.md
step 1, merged) and the `agreement` link on Contract / StructuredContract
(step 2, merged).

Same static-method + ApiConnection style as
energydeskapi/contracts/contracts_api.py::ContractsApi.

Endpoint paths are the ones from the appserver's actual urls.py
(energydesk/apps/agreements/urls.py), which match the plan's REST table.
`get_contracts_by_agreement` is a thin pass-through onto the existing
contracts list/embedded endpoints with an `agreement` query parameter -
note that filter is not yet wired server-side (trade_filters.py doesn't
have it; it's an open item from the step-2 PR), so this call will 400 or
silently ignore the parameter until that lands. Included now so callers
don't need to change once it does.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from energydeskapi.sdk.api_connection import ApiConnection

logger = logging.getLogger(__name__)


class AgreementsApi:
    """Trading accounts and master agreements."""

    @staticmethod
    def get_trading_accounts(api_connection: ApiConnection, parameters: dict = {}) -> Any:
        logger.info("Listing trading accounts")
        return api_connection.exec_get_url("/api/agreements/trading-accounts/", parameters)

    @staticmethod
    def get_trading_accounts_embedded(api_connection: ApiConnection, parameters: dict = {}) -> Any:
        logger.info("Listing trading accounts embedded")
        return api_connection.exec_get_url("/api/agreements/trading-accounts/embedded/", parameters)

    @staticmethod
    def get_trading_account(api_connection: ApiConnection, trading_account_pk: int) -> Any:
        logger.info("Loading trading account %s", trading_account_pk)
        return api_connection.exec_get_url(f"/api/agreements/trading-accounts/{trading_account_pk}/")

    @staticmethod
    def get_trading_account_credit(api_connection: ApiConnection, trading_account_pk: int) -> Any:
        """Resolved, read-only credit profile - see
        energydeskapi.types.agreements.CreditProfile for the wire shape."""
        logger.info("Loading credit profile for trading account %s", trading_account_pk)
        return api_connection.exec_get_url(f"/api/agreements/trading-accounts/{trading_account_pk}/credit/")

    @staticmethod
    def get_master_agreements(api_connection: ApiConnection, parameters: dict = {}) -> Any:
        logger.info("Listing master agreements")
        return api_connection.exec_get_url("/api/agreements/master-agreements/", parameters)

    @staticmethod
    def get_master_agreements_embedded(api_connection: ApiConnection, parameters: dict = {}) -> Any:
        logger.info("Listing master agreements embedded")
        return api_connection.exec_get_url("/api/agreements/master-agreements/embedded/", parameters)

    @staticmethod
    def get_master_agreement(api_connection: ApiConnection, master_agreement_pk: int) -> Any:
        logger.info("Loading master agreement %s", master_agreement_pk)
        return api_connection.exec_get_url(f"/api/agreements/master-agreements/{master_agreement_pk}/")

    @staticmethod
    def get_election_sheets(api_connection: ApiConnection, parameters: dict = {}) -> Any:
        logger.info("Listing election sheets")
        return api_connection.exec_get_url("/api/agreements/election-sheets/", parameters)

    @staticmethod
    def get_credit_support_annexes(api_connection: ApiConnection, parameters: dict = {}) -> Any:
        logger.info("Listing credit support annexes")
        return api_connection.exec_get_url("/api/agreements/credit-support-annexes/", parameters)

    @staticmethod
    def get_contracts_by_agreement(
        api_connection: ApiConnection, agreement_pk: int, embedded: bool = False, parameters: Optional[dict] = None
    ) -> Any:
        """Contracts booked under one MasterAgreement.

        See module docstring - the `agreement` filter is not wired into
        trade_filters.py yet (open item from the step-2 PR).
        """
        params = dict(parameters or {})
        params["agreement"] = agreement_pk
        suburl = "/api/portfoliomanager/contracts/embedded/" if embedded else "/api/portfoliomanager/contracts/"
        logger.info("Listing contracts for agreement %s", agreement_pk)
        return api_connection.exec_get_url(suburl, params)

    @staticmethod
    def get_structured_contracts_for_contracts(
        api_connection: ApiConnection, contract_pks: list[int], parameters: Optional[dict] = None
    ) -> Any:
        """Structured-contract satellites for a set of booked contracts."""
        params = dict(parameters or {})
        params["contract__in"] = ",".join(str(pk) for pk in contract_pks)
        logger.info("Listing structured contracts for %d contract(s)", len(contract_pks))
        return api_connection.exec_get_url("/api/origination/structured/embedded/", params)
