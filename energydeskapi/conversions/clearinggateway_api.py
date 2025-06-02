import json
import logging
from dataclasses import dataclass
from typing import Optional

import environ

from energydeskapi.conversions.elvizlink_api import ElvizLinksApi

logger = logging.getLogger(__name__)

#  Change
class ClearingGatewayApi:
    @staticmethod
    def exec_fetch_deal_data(trading_date: Optional[str]) -> list[dict[str,any]]:
        env = environ.Env()
        server_url = None if 'ELVIZ_PROXY' not in env else f"{env.str('ELVIZ_PROXY')}/clearinggateway/api/clearinggateway/get_deal_data"
        logger.info(f"Calling clearing gateway URL {server_url}")
        h = {'Authorization': 'Bearer', 'Accept': 'application/json'}
        authsess = ElvizLinksApi.obtain_session()
        response = authsess.get(server_url, headers=h, params={} if trading_date is None else {'trading_date': trading_date})
        return json.loads(response.text)


