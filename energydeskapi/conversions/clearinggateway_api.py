import json
import logging
from dataclasses import dataclass

import environ

from energydeskapi.conversions.elvizlink_api import ElvizLinksApi

logger = logging.getLogger(__name__)

#  Change
class ClearingGatewayApi:
    @staticmethod
    def exec_fetch_deal_data() -> list[dict[str,any]]:
        env = environ.Env()
        server_url = None if 'ELVIZ_PROXY' not in env else f"{env.str('ELVIZ_PROXY')}/clearinggateway/api/clearinggateway/getdealdata"
        logger.info(f"Calling clearing gateway URL {server_url}")
        h = {'Authorization': 'Bearer', 'Accept': 'application/json'}
        authsess = ElvizLinksApi.obtain_session()
        response = authsess.get(server_url, headers=h)
        return json.loads(response.text)


