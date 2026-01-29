import json
import logging
from dataclasses import dataclass
from datetime import date
from typing import Optional

import environ

from energydeskapi.conversions.elvizlink_api import ElvizLinksApi
from energydeskapi.sdk.common_utils import not_nones_in_list, not_nones_in_dict_values

logger = logging.getLogger(__name__)

#  Change
class MontelApi:
    @staticmethod
    def exec_reload_products() -> str:
        server_url = MontelApi._build_server_url("reload-products")
        logger.info(f"Calling montel service URL {server_url}")
        h = {'Authorization': 'Bearer', 'Accept': 'application/json'}
        authsess = ElvizLinksApi.obtain_session()
        response = authsess.post(server_url, headers=h)
        return response.text

    @staticmethod
    def exec_download_historical_internally(period_from: date, period_until: date, match_ticker: Optional[str] = None) -> dict:
        server_url = MontelApi._build_server_url(f"download_historical")
        logger.info(f"Calling montel service URL {server_url} to download historical prices internally in Montel service")
        h = {'Authorization': 'Bearer', 'Accept': 'application/json'}
        authsess = ElvizLinksApi.obtain_session()
        response = authsess.post(server_url, headers=h, data=not_nones_in_dict_values({
            "from": period_from.isoformat(),
            "until": period_until.isoformat(),
            "match_ticker": match_ticker
        }))
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Response: {response}")
        return response.text

    @staticmethod
    def exec_get_historical(period_from: date, period_until: date, match_ticker: Optional[str] = None) -> dict:
        server_url = MontelApi._build_server_url("historical")
        logger.info(f"Calling montel service URL {server_url} to get the historical prices from the Montel service own database")
        h = {'Authorization': 'Bearer', 'Accept': 'application/json'}
        authsess = ElvizLinksApi.obtain_session()
        response = authsess.get(server_url, headers=h, params=not_nones_in_dict_values({
            'from': period_from.isoformat(),
            'until':period_until.isoformat(),
            'match_ticker': match_ticker
        }))
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Response: {response}")
        return response.text

    @staticmethod
    def _build_server_url(path: str) -> Optional[str]:
        env = environ.Env()
        return None if 'ELVIZ_PROXY' not in env else f"{env.str('ELVIZ_PROXY')}/montel/api/montelservice/{path}"


