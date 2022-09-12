import requests
import json
import logging
import pandas as pd
from energydeskapi.marketdata.markets_api import MarketsApi
logger = logging.getLogger(__name__)


class ProductsApi:
    """Class for user profiles and companies

    """



    @staticmethod
    def get_products(api_connection, market_enum):
        """Fetches all company objects with URL relations. Will only return companies for which the user has rights

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        mapi=MarketsApi.get_market_object(api_connection, market_enum)
        print(mapi)
        logger.info("Fetching products in market " + str(market))
        qry_payload = {
            #"market_place": None,
            "market_name": mapi['name'],
            #"tradingdate_from": None,
        }
        json_res=api_connection.exec_post_url('/api/markets/traded_products/',qry_payload)
        if json_res is None:
            return None
        return json_res
