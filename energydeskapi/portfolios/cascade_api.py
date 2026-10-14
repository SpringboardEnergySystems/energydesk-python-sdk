import json
import logging
from typing import Any, Optional

from energydeskapi.sdk.api_connection import ApiConnection

logger = logging.getLogger(__name__)

CASCADING_URL = '/api/portfoliomanager/cascading'


class CascadeApiError(Exception):
    """The appserver refused or failed a cascading call.

    Carries what a proxy needs to relay the answer unchanged: the HTTP status, the human-readable ``detail``
    and the parsed JSON ``body`` (for an aborted execute this holds the ``report``). 401/403 are not wrapped:
    they surface as TokenException / AuthorizationFailedException like in every other SDK API.
    """

    def __init__(self, status_code: Optional[int], detail: str, body: Optional[dict] = None):
        super().__init__(f"Cascading call failed ({status_code}): {detail}")
        self.status_code = status_code
        self.detail = detail
        self.body = body


def _error_from(status_code: Optional[int], error_text: Optional[str]) -> CascadeApiError:
    try:
        body = json.loads(error_text) if error_text else None
    except ValueError:
        body = None
    if isinstance(body, dict):
        return CascadeApiError(status_code, str(body.get("detail", error_text)), body)
    return CascadeApiError(status_code, error_text or "", None)


class CascadeApi:
    """Pass-through wrappers for the appserver cascading endpoints (EDETRM-78). They add no logic: validation,
    the simulation guardrail and the access check (SystemFeaturesEnum.CASCADING) all live in the appserver."""

    @staticmethod
    def _post(api_connection: ApiConnection, action: str, payload: dict) -> dict:
        success, json_res, status_code, error_text = api_connection.exec_post_url(f"{CASCADING_URL}/{action}/", payload=payload)
        if not success:
            raise _error_from(status_code, error_text)
        return json_res

    @staticmethod
    def simulate_cascade(api_connection: ApiConnection, params: dict[str, Any]) -> dict:
        """Runs a cascade simulation; nothing is stored. Returns the report (log, errors, contracts that would be generated).

        ``params``: contract_type (FUTURE|BILATERAL|FORWARD), cascade_date (YYYY-MM-DD), trading_book_ids (list of int),
        period_from (QUARTER|YEAR), market_place (NASDAQ_OMX|EEX|EURONEXT), and optionally price_mode
        (ORIGINAL_COST|LAST_CLOSE) and ticker_contains.
        """
        logger.info("Simulating cascade")
        return CascadeApi._post(api_connection, "simulate", params)

    @staticmethod
    def execute_cascade(api_connection: ApiConnection, params: dict[str, Any]) -> dict:
        """Cascades for real; same ``params`` as simulate_cascade. The appserver refuses (CascadeApiError, 409) unless an
        error-free simulation of the same parameters was run recently, and rolls everything back if the run fails."""
        logger.info("Executing cascade")
        return CascadeApi._post(api_connection, "execute", params)

    @staticmethod
    def list_cascade_processes(api_connection: ApiConnection, trading_book: Optional[int] = None,
                               limit: Optional[int] = None) -> list[dict]:
        """Cascade processes, newest first, with parameters, contract counts and a ``reversible`` flag."""
        parameters: dict[str, Any] = {}
        if trading_book is not None:
            parameters["trading_book"] = trading_book
        if limit is not None:
            parameters["limit"] = limit
        json_res = api_connection.exec_get_url(f"{CASCADING_URL}/processes/", parameters)
        if json_res is None:  # exec_get_url does not expose the status of a failed GET
            raise CascadeApiError(None, "Listing cascade processes failed")
        return json_res

    @staticmethod
    def undo_cascade(api_connection: ApiConnection, process_id: int, simulation: bool) -> dict:
        """Reverses a cascade process. ``simulation`` is required: True only reports what would be deleted."""
        logger.info(f"Undoing cascade process {process_id} (simulation: {simulation})")
        return CascadeApi._post(api_connection, "undo", {"process_id": process_id, "simulation": simulation})
