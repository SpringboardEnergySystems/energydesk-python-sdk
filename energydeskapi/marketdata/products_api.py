import requests
import json
import logging
import pandas as pd
from energydeskapi.marketdata.markets_api import MarketsApi
logger = logging.getLogger(__name__)


class Product:
    def __init__(self):
        self.pk=0
        self.ticker=None
        self.vendor_ticker=None
        self.description=""
        self.area=None
        self.denomination=None
        self.base_peak=None
        self.spread=None
        self.otc=None
        self.delivery_from=""
        self.delivery_until=""
        self.contract_size=None
        self.traded_from=None
        self.traded_until = None
        self.instrument_type = None
        self.commodity_type = None
        self.block_size_category = None
        self.market = None
        self.market_place = None

class ProductsApi:
    """Class for products in markets

    """

    # This function returns a single price (avg) for the period requested
    @staticmethod
    def register_products(api_connection, product_list):
        """ Registers assets

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param asset_list: list of assets
        :type asset_list: str, required
        """
        logger.info("Registering " + str(len(product_list) )+ " products")
        for product in product_list:
            payload={}
            if product.ticker is not None: payload['ticker']=product.ticker
            if product.vendor_ticker is not None: payload['vendor_ticker']=product.vendor_ticker
            if product.description is not None: payload['description'] = product.description
            if product.area is not None: payload['area'] = product.area
            if product.denomination is not None: payload['denomination'] = product.denomination
            if product.base_peak is not None: payload['base_peak'] = product.base_peak
            if product.spread is not None: payload['spread'] = product.spread
            if product.otc is not None: payload['otc'] = product.otc
            if product.delivery_from is not None: payload['delivery_from'] = product.delivery_from
            if product.delivery_until is not None: payload['delivery_until'] = product.delivery_until
            if product.contract_size is not None: payload['contract_size'] = product.contract_size
            if product.traded_from is not None: payload['traded_from'] = product.traded_from
            if product.traded_until is not None: payload['traded_until'] = product.traded_until
            if product.instrument_type is not None: payload['instrument_type'] = product.instrument_type
            if product.commodity_type is not None: payload['commodity_type'] = product.commodity_type
            if product.block_size_category is not None: payload['block_size_category'] = product.block_size_category
            if product.market is not None: payload['market'] = product.market
            if product.block_size_category is not None: payload['block_size_category'] = product.block_size_category
            json_res=api_connection.exec_post_url('/api/markets/marketproducts/', payload)
            if json_res is None:
                return False
            print(json_res)
    @staticmethod
    def get_products(api_connection, market_enum):
        """Fetches all company objects with URL relations. Will only return companies for which the user has rights

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        mapi=MarketsApi.get_market_object(api_connection, market_enum)
        print(mapi)
        logger.info("Fetching products in market " +mapi['name'])
        qry_payload = {
            #"market_place": None,
            "market_name": mapi['name'],
            #"tradingdate_from": None,
        }
        json_res=api_connection.exec_post_url('/api/markets/query_products/',qry_payload)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_products_verbose(api_connection, market_enum):
        """Fetches all company objects with URL relations. Will only return companies for which the user has rights

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        mapi=MarketsApi.get_market_object(api_connection, market_enum)
        print(mapi)
        logger.info("Fetching products in market " +mapi['name'])
        qry_payload = {
            #"market_place": None,
            "market_name": mapi['name'],
            #"tradingdate_from": None,
        }
        json_res=api_connection.exec_post_url('/api/markets/query_products_ext/',qry_payload)
        if json_res is None:
            return None
        #df = pd.DataFrame(data=json_res)
        df = pd.DataFrame.from_dict(json_res, orient='columns')
        return df