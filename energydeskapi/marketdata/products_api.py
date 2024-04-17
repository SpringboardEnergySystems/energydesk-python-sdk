import logging
import pandas as pd
from energydeskapi.types.market_enum_types import MarketEnum, MarketPlaceEnum
from energydeskapi.marketdata.markets_api import MarketsApi
from energydeskapi.marketdata.product_utils import convert_productjson_dataframe
from energydeskapi.types.market_enum_types import MarketEnum
logger = logging.getLogger(__name__)

class Singleton(object):
  _instances = {}
  def __new__(class_, *args, **kwargs):
    if class_ not in class_._instances:
        class_._instances[class_] = super(Singleton, class_).__new__(class_, *args, **kwargs)
    return class_._instances[class_]

class ProductHelper(Singleton):
    product_map={}
    def __init__(self):
        pass

    def resolve_ticker(self, api_conn, ticker):
        if ticker in self.product_map:
            return self.product_map[ticker]
        res = ProductsApi.get_market_products(api_conn, {'market_ticker': ticker})
        if len(res['results']) == 0:
            logger.info( {'need to generate product from market_ticker': ticker})
            res = ProductsApi.generate_market_product_from_ticker(api_conn, MarketPlaceEnum.NASDAQ_OMX.name, ticker)
            if res[0] == False:
                logger.error(f"Error generating product from ticker {res}")
            k = res[1][0]['pk']
        else:
            k = res['results'][0]['pk']
        self.product_map[ticker]=k
        return k

class Product:
    def __init__(self):
        self.pk=0
        self.ticker=None
        self.vendor_ticker=None
        self.description=""
        self.area="SYS"
        self.denomination=None
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
        self.market = MarketEnum.NORDIC_POWER.name
        self.market_place = None
        self.delivery_type="FINANCIAL"
        self.commodity_profile="BASELOAD"

    def get_dict(self):
        dict = {}
        commodity = {}
        dict['pk']=self.pk
        if self.ticker is not None: dict['market_ticker'] = self.ticker
        if self.ticker is not None: commodity['product_code'] = self.ticker
        if self.vendor_ticker is not None: dict['vendor_ticker'] = self.vendor_ticker
        if self.description is not None: commodity['description'] = self.description
        if self.area is not None: commodity['area'] = self.area
        if self.denomination is not None: dict['denomination'] = self.denomination
        if self.commodity_profile is not None: commodity['commodity_profile'] = self.commodity_profile
        if self.delivery_type is not None: commodity['delivery_type'] = self.delivery_type
        if self.spread is not None: commodity['spread'] = self.spread
        if self.otc is not None: commodity['otc'] = self.otc
        if self.delivery_from is not None: commodity['delivery_from'] = self.delivery_from
        if self.delivery_until is not None: commodity['delivery_until'] = self.delivery_until
        if self.contract_size is not None: commodity['contract_size'] = self.contract_size
        if self.traded_from is not None: dict['traded_from'] = self.traded_from
        if self.traded_until is not None: dict['traded_until'] = self.traded_until
        if self.instrument_type is not None: commodity['instrument_type'] = self.instrument_type
        if self.commodity_type is not None: commodity['commodity_type'] = self.commodity_type
        if self.block_size_category is not None: commodity['block_size_category'] = self.block_size_category
        if self.market is not None: commodity['market'] = self.market
        if self.block_size_category is not None: commodity['block_size_category'] = self.block_size_category
        dict['commodity_definition'] = commodity
        return dict
class ProductsApi:
    """Class for products in markets

    """

    @staticmethod
    def get_commodity_definitioon_url(api_connection, commodity_deinition_pk):
        """Fetches url for tradingbook from pk

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param tradingbook_pk: personal key of tradingbook
        :type tradingbook_pk: str, required
        """
        return api_connection.get_base_url() + '/api/markets/commoditydefinitions/' + str(commodity_deinition_pk) + "/"

    @staticmethod
    def get_commodity_definitions(api_connection, parameters={}):
        json_res = api_connection.exec_get_url('/api/markets/commoditydefinitions/', parameters)
        if json_res is None:
            return False
        return json_res

    @staticmethod
    def get_market_products(api_connection, parameters={}):
        json_res = api_connection.exec_get_url('/api/markets/marketproducts/', parameters)
        if json_res is None:
            return False
        return json_res

    @staticmethod
    def get_market_products_embedded(api_connection, parameters={}):
        json_res = api_connection.exec_get_url('/api/markets/marketproducts/embedded/', parameters)
        if json_res is None:
            return False
        return json_res

    @staticmethod
    def get_product_prices(api_connection, parameters={}):
        json_res = api_connection.exec_get_url('/api/markets/productprices/', parameters)
        if json_res is None:
            return False
        return json_res

    @staticmethod
    def get_product_prices_embedded(api_connection, parameters={}):
        json_res = api_connection.exec_get_url('/api/markets/productprices/embedded/', parameters)
        if json_res is None:
            return False
        return json_res

    @staticmethod
    def get_market_products_df(api_connection, parameters={}):
        json_res=ProductsApi.get_market_products_embedded(api_connection, parameters)
        return convert_productjson_dataframe(json_res)

    @staticmethod
    def generate_market_product_from_ticker(api_connection, market, market_ticker):
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/markets/gen-marketproduct/',
                                                {'market_ticker':market_ticker, 'market':market})
        print(status_code, json_res)
        return success, json_res, status_code, error_msg

    @staticmethod
    def register_commodity(api_connection, commodity_definition):
        """Registers products

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param product_list: list of products
        :type product_list: str, required
        """

        success, json_res, status_code, error_msg=api_connection.exec_post_url('/api/markets/commoditydefinitions/', commodity_definition)
        if json_res is None:
            return 0
        print(json_res)
        return json_res['pk']
    @staticmethod
    def register_products(api_connection, product_list):
        """Registers products

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param product_list: list of products
        :type product_list: str, required
        """
        logger.info("Registering " + str(len(product_list) )+ " products")
        for product in product_list:
            payload=product.get_dict()
            key=ProductsApi.register_commodity(api_connection,payload['commodity_definition'])
            if key==0:
                return False
            payload['commodity_definition']=ProductsApi.get_commodity_definitioon_url(api_connection, key)
            print("REG PROD ", payload)
            success, json_res, status_code, error_msg=api_connection.exec_post_url('/api/markets/marketproducts/', payload)
            if json_res is None:
                return False
            print(json_res)
    @staticmethod
    def get_products(api_connection, market_enum):
        """Fetches products from markets

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param market_enum: markets
        :type market_enum: str, required
        """
        mapi=MarketsApi.get_market_obj(api_connection, market_enum)
        print(mapi)
        logger.info("Fetching products in market " +mapi['name'])
        qry_payload = {
            #"market_place": None,
            "market_name": mapi['name'],
            #"tradingdate_from": None,
        }
        success, json_res, status_code, error_msg=api_connection.exec_post_url('/api/markets/query-products/',qry_payload)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_products_df(api_connection, market_enum):
        """Fetches products from markets and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param market_enum: markets
        :type market_enum: str, required
        """
        mapi=MarketsApi.get_market_obj(api_connection, market_enum)

        logger.info("Fetching products in market " +mapi['name'])
        qry_payload = {
            #"market_place": None,
            "market_name": mapi['name'],
            #"tradingdate_from": None,
        }
        success, json_res, status_code, error_msg=api_connection.exec_post_url('/api/markets/query-products-ext/',qry_payload)
        if json_res is None:
            return None
        #df = pd.DataFrame(data=json_res)
        df = pd.DataFrame.from_dict(json_res, orient='columns')
        return df