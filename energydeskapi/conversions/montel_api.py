import json
import logging
from dataclasses import dataclass

import environ

from energydeskapi.conversions.elvizlink_api import ElvizLinksApi

logger = logging.getLogger(__name__)

#  Change
class MontelApi:
    @staticmethod
    def exec_reload_products() -> str:
        env = environ.Env()
        server_url = None if 'ELVIZ_PROXY' not in env else f"{env.str('ELVIZ_PROXY')}/montel/api/montelservice/reload-products"
        logger.info(f"Calling montel service URL {server_url}")
        h = {'Authorization': 'Bearer', 'Accept': 'application/json'}
        authsess = ElvizLinksApi.obtain_session()
        response = authsess.post(server_url, headers=h)
        return response.text


