import json
import logging
from dataclasses import dataclass
from typing import Optional

import environ

from energydeskapi.conversions.elvizlink_api import ElvizLinksApi

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
    def exec_get_historical() -> dict:
        server_url = MontelApi._build_server_url("historical")
        logger.info(f"Calling montel service URL {server_url}")
        h = {'Authorization': 'Bearer', 'Accept': 'application/json'}
        authsess = ElvizLinksApi.obtain_session()
        response = authsess.get(server_url, headers=h)
        return response.json()

    @staticmethod
    def _build_server_url(path: str) -> Optional[str]:
        env = environ.Env()
        return None if 'ELVIZ_PROXY' not in env else f"{env.str('ELVIZ_PROXY')}/montel/api/montelservice/{path}"


