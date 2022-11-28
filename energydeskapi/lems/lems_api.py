import logging
import pandas as pd
import logging
import pandas as pd
from datetime import datetime, timedelta
from energydeskapi.marketdata.markets_api import MarketsApi
from energydeskapi.sdk.datetime_utils import convert_datime_to_utcstr
logger = logging.getLogger(__name__)


def check_fix_date2str(dt):
    if isinstance(dt, str):
        return dt
    return convert_datime_to_utcstr(dt)


class LocalProduct:
    """ Class for local product

    """

    def __init__(self,
                 local_market=None,
                 local_area=None,
                 ticker=None,
                 description=None,
                 currency=None,
                 traded_from=None,
                 traded_until=None,
                 commodity_type=None,
                 instrument_type=None,
                 contract_status=None,
                 buy_or_sell=None,
                 counterpart=None,
                 market=None,
                 trader=None,
                 marketplace_product=None
                 ):
        self.pk = 0
        self.local_market = local_market
        self.local_area = local_area
        self.ticker = ticker
        self.description = description
        self.currency = currency
        self.traded_from = traded_from
        self.traded_until = traded_until
        self.commodity_type = commodity_type
        self.instrument_type = instrument_type
        self.contract_status = contract_status
        self.buy_or_sell = buy_or_sell
        self.counterpart = counterpart
        self.market = market
        self.trader = trader
        self.marketplace_product = marketplace_product
        self.commodity_delivery_from = None
        self.commodity_delivery_until = None
        self.product_code = None
        self.otc_multi_delivery_periods = []
        self.tags = []
        self.area = "SYS"
        self.base_peak = "BASE"
        self.spread = False
        self.otc = False

    def get_dict(self, api_conn):
        dict = {}
        dict['pk'] = self.pk
        prod = {}
        if self.instrument_type is not None:
            prod['instrument_type'] = MarketsApi.get_instrument_type_url(
                api_conn, self.instrument_type)
        if self.commodity_type is not None:
            prod['commodity_type'] = MarketsApi.get_commodity_type_url(
                api_conn, self.commodity_type)
        if self.commodity_delivery_from is not None:
            prod['delivery_from'] = check_fix_date2str(
                self.commodity_delivery_from)
        if self.commodity_delivery_until is not None:
            prod['delivery_until'] = check_fix_date2str(
                self.commodity_delivery_until)
        prod['area'] = self.area
        prod['base_peak'] = self.base_peak
        prod['spread'] = self.spread
        prod['otc'] = self.otc

        if self.ticker is not None:
            prod['product_code'] = self.ticker
        else:
            prod['otc'] = True
        dict['commodity_definition'] = prod
        dict['ticker'] = self.ticker
        dict['local_market'] = self.local_market
        dict['local_area'] = self.local_area
        dict['currency'] = self.currency
        dict['traded_from'] = check_fix_date2str(self.traded_from)
        dict['traded_until'] = check_fix_date2str(self.traded_until)
        return dict


class LemsApi:
    """Class for price curves

    """
    @staticmethod
    def upsert_localmarket(api_connection, description, operator_url, areas):
        """Registers local marketplace

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Registering local market")
        payload = {
            "description": description,
            "operator": operator_url,
            "local_areas": areas
        }
        success, json_res, status_code, error_msg = api_connection.exec_post_url(
            '/api/lems/localmarkets/', payload)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_local_markets(api_connection, params={}):
        """Fetches url for location type from pk

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param key: personal key
        :type key: str, required
        """

        json_res = api_connection.exec_get_url('/api/lems/localmarkets/', params)
        return json_res

    @staticmethod
    def get_local_market_url(api_connection, key):
        """Fetches url for location type from pk

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param key: personal key
        :type key: str, required
        """
        return api_connection.get_base_url() + '/api/lems/localmarkets/' + str(
            key) + "/"

    @staticmethod
    def upsert_localproduct(api_connection, local_product):
        """Registers local local product

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Registering local product")
        payload = local_product.get_dict(api_connection)
        print(payload)
        success, json_res, status_code, error_msg = api_connection.exec_post_url(
            '/api/lems/localproducts/', payload)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def get_ticker_data(api_connection, area=None):
        """Fetches all counterparts and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching counterparts list")
        if area == None:
            area = "NO1"
        json_res = api_connection.exec_get_url(
            '/api/lems/tickerdata?area=' + area)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def get_traded_products(api_connection, parameters={}):
        """Fetches all counterparts and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching counterparts list")
        json_res = api_connection.exec_get_url(
            '/api/lems/localproducts/compact/', parameters)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def add_order(api_connection, ticker, price, currency, quantity, buy_or_sell, order_type="NORMAL", expiry=None):
        """Fetches all counterparts and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        exp = (datetime.today() + timedelta(days=2)
               ).replace(hour=0, minute=0, second=0, microsecond=0)
        expiry_str = check_fix_date2str(
            exp) if expiry is None else check_fix_date2str(expiry)
        payload = {
            # "order_id":"",# Will be set by server
            # "order_timestamp":"", # Will be set by server
            "ticker": ticker,
            "price": price,
            "currency": currency,
            "quantity": quantity,
            "expiry": expiry_str,
            "buy_or_sell": buy_or_sell,
            "order_type": order_type
        }
        print(payload)
        success, json_res, status_code, error_msg = api_connection.exec_post_url(
            '/api/lems/addorder/', payload)
        if not success:
            logger.error(error_msg)
        return success, json_res, status_code, error_msg

    @staticmethod
    def remove_order(api_connection, ticker, order_id):
        """Fetches all counterparts and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        payload = {
            "ticker": ticker,
            "order_id": order_id,
        }

        success, json_res, status_code, error_msg = api_connection.exec_post_url(
            '/api/lems/removeorder/', payload)

        return success

    @staticmethod
    def query_active_orders(api_connection, ticker=None):
        """Fetches all counterparts and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """

        logger.info("Query orders")
        url = '/api/lems/liveorders/' if ticker is None else '/api/lems/liveorders/?ticker=' + ticker
        json_res = api_connection.exec_get_url(url)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def query_own_orders(api_connection, ticker=None):
        """Fetches all counterparts and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """

        logger.info("Query own orders")
        url = '/api/lems/myorders/' if ticker is None else '/api/lems/myorders/?ticker=' + ticker
        json_res = api_connection.exec_get_url(url)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def query_own_trades(api_connection, ticker=None):
        """Fetches all counterparts and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """

        logger.info("Query own trades")
        url = '/api/lems/mytrades/' if ticker is None else '/api/lems/mytrades/?ticker=' + ticker
        json_res = api_connection.exec_get_url(url)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df
