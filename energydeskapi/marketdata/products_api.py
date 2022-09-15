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

    def get_dict(self):
        dict = {}
        dict['pk']=self.pk
        if self.ticker is not None: dict['ticker'] = self.ticker
        if self.vendor_ticker is not None: dict['vendor_ticker'] = self.vendor_ticker
        if self.description is not None: dict['description'] = self.description
        if self.area is not None: dict['area'] = self.area
        if self.denomination is not None: dict['denomination'] = self.denomination
        if self.base_peak is not None: dict['base_peak'] = self.base_peak
        if self.spread is not None: dict['spread'] = self.spread
        if self.otc is not None: dict['otc'] = self.otc
        if self.delivery_from is not None: dict['delivery_from'] = self.delivery_from
        if self.delivery_until is not None: dict['delivery_until'] = self.delivery_until
        if self.contract_size is not None: dict['contract_size'] = self.contract_size
        if self.traded_from is not None: dict['traded_from'] = self.traded_from
        if self.traded_until is not None: dict['traded_until'] = self.traded_until
        if self.instrument_type is not None: dict['instrument_type'] = self.instrument_type
        if self.commodity_type is not None: dict['commodity_type'] = self.commodity_type
        if self.block_size_category is not None: dict['block_size_category'] = self.block_size_category
        if self.market is not None: dict['market'] = self.market
        if self.block_size_category is not None: dict['block_size_category'] = self.block_size_category
        return dict
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
            payload=product.get_dict()
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
        mapi=MarketsApi.get_market_obj(api_connection, market_enum)
        print(mapi)
        logger.info("Fetching products in market " +mapi['name'])
        qry_payload = {
            #"market_place": None,
            "market_name": mapi['name'],
            #"tradingdate_from": None,
        }
        json_res=api_connection.exec_post_url('/api/markets/query-products/',qry_payload)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_products_verbose(api_connection, market_enum):
        """Fetches all company objects with URL relations. Will only return companies for which the user has rights

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        mapi=MarketsApi.get_market_obj(api_connection, market_enum)
        print(mapi)
        logger.info("Fetching products in market " +mapi['name'])
        qry_payload = {
            #"market_place": None,
            "market_name": mapi['name'],
            #"tradingdate_from": None,
        }
        json_res=api_connection.exec_post_url('/api/markets/query-products-ext/',qry_payload)
        if json_res is None:
            return None
        #df = pd.DataFrame(data=json_res)
        df = pd.DataFrame.from_dict(json_res, orient='columns')
        return df