import requests
import json
import logging
import pandas as pd
logger = logging.getLogger(__name__)



class LocalProduct:
    """ Class for local product

    """
    def __init__(self,
                 local_market=None,
                 local_area=None,
                 ticker=None,
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
        self.pk=0
        self.local_market=local_market
        self.local_area=local_area
        self.ticker=ticker
        self.currency = currency
        self.traded_from=traded_from
        self.traded_until=traded_until
        self.commodity_type=commodity_type
        self.instrument_type=instrument_type
        self.contract_status=contract_status
        self.buy_or_sell=buy_or_sell
        self.counterpart=counterpart
        self.market=market
        self.trader=trader
        self.marketplace_product=marketplace_product
        self.commodity_delivery_from = None
        self.commodity_delivery_until = None
        self.product_code=None
        self.otc_multi_delivery_periods=[]
        self.tags=[]
        self.area="SYS"
        self.base_peak = "BASE"
        self.spread = False
        self.otc = False

    fields = ['pk', 'local_market', 'local_area', 'ticker', 'currency', 'traded_from', 'traded_until',
              'commodity_definition']

    def get_dict(self, api_conn):
        dict = {}
        dict['pk'] = self.pk
        prod = {}
       # if self.instrument_type is not None: prod['instrument_type'] = MarketsApi.get_instrument_type_url(api_conn,self.instrument_type)
       # if self.commodity_type is not None: prod['commodity_type'] = MarketsApi.get_commodity_type_url(api_conn, self.commodity_type)
       # if self.commodity_delivery_from is not None:prod['delivery_from'] = check_fix_date2str(self.commodity_delivery_from)
       # if self.commodity_delivery_until is not None: prod['delivery_until'] = check_fix_date2str(self.commodity_delivery_until)
        prod['area']=self.area
        prod['base_peak'] = self.base_peak
        prod['spread'] = self.spread
        prod['otc'] = self.otc
        if self.product_code is not None:
            prod['product_code'] = self.product_code
        else:
            prod['otc'] = True
        dict['commodity_definition']=prod

class LemsApi:
    """Class for price curves

    """
    @staticmethod
    def upsert_localmarket(api_connection, description, operator_url):
        """Registers local marketplace

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Registering local market")
        payload={
            "descrption":description,
            "operator":operator_url
        }
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/lems/localmarkets/', payload)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def upsert_localproduct(api_connection, description, operator_url):
        """Registers local local product

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Registering local product")
        payload={
            "descrption":description,
            "operator":operator_url
        }
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/lems/localproducts/', payload)
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
        if area==None:
            area="NO1"
        json_res = api_connection.exec_get_url('/api/lems/tickerdata?area=' + area)
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
        json_res = api_connection.exec_get_url('/api/lems/localproducts/compact/', parameters)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def add_order(api_connection, ticker, price, quantity, buy_or_sell):
        """Fetches all counterparts and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        payload={
            "order_id":"",
            "order_timestamp":"2022-01-23",
            "ticker":ticker,
            "price":price,
            "quantity": quantity,
            "buy_or_sell":buy_or_sell
        }
        logger.info("Enter orde")
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/lems/addorder/', payload)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df


    @staticmethod
    def remove_order(api_connection, ticker, order_id):
        """Fetches all counterparts and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        payload={
            "ticker":ticker,
            "order_id":order_id,
        }

        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/lems/removeorder/', payload)

        return success

    @staticmethod
    def query_active_orders(api_connection, ticker):
        """Fetches all counterparts and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """

        logger.info("Query orders")
        json_res=api_connection.exec_get_url('/api/lems/liveorders/?ticker=' + ticker)
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
        url='/api/lems/myorders/' if ticker is None else '/api/lems/myorders/?ticker=' + ticker
        json_res=api_connection.exec_get_url(url)
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
        json_res=api_connection.exec_get_url(url)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df