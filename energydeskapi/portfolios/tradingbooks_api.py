import requests
import json
import logging
import pandas as pd


logger = logging.getLogger(__name__)
#  Change

class TradingBook():
    def __init__(self):
        self.pk=0
        self.description=None
        self.asset=None
        self.manager=None
        self.contract_types=[]
        self.commodity_types=[]
        self.traders=[]
    def get_dict(self):
        dict = {}
        dict['pk']=self.pk
        if self.description is not None: dict['description'] = self.description
        if self.asset is not None: dict['asset'] = self.asset
        if self.manager is not None: dict['manager'] = self.manager
        if self.contract_types is not None: dict['contract_types'] = self.contract_types
        if self.commodity_types is not None: dict['commodity_types'] = self.commodity_types
        if self.traders is not None: dict['traders'] = self.traders
        return dict

class TradingBooksApi:
    """Class for tradingbooks

      """



    @staticmethod
    def get_tradingbooks(api_connection, parameters={}):
        """Fetches all tradingbooks

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching trading books")
        json_res = api_connection.exec_get_url('/api/portfoliomanager/tradingbooks/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_tradingbooks_df(api_connection, parameters={}):
        """Fetches all tradingbooks and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        parameters['page_size']=1000
        json_res=TradingBooksApi.get_tradingbooks(api_connection, parameters)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res['results'])
        return df

    @staticmethod
    def get_tradingbooks_by_commodityfilter(api_connection, commodities,parameters={}):
        """Fetches tradingbooks from commodity filter

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param commodities: all commodities
        :type commodities: str, required
        """
        def commodities_as_str():
            strval=""
            for c in commodities:
                com = c if isinstance(c, int) else c.value
                strval=strval + str(com) + ","
            if len(strval)>1:
                strval=strval[:-1]  #Get rid of the last ,
            return strval

        parameters["commodity_types"]=commodities_as_str()
        res = TradingBooksApi.get_tradingbooks(api_connection, parameters)
        return res

    @staticmethod
    def get_tradingbooks_by_commodityfilter_df(api_connection, commodities, parameters={}):
        """Fetches tradingbooks from commodity filter and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param commodities: all commodities
        :type commodities: str, required
        """
        parameters['page_size']=100
        json_res = TradingBooksApi.get_tradingbooks_by_commodityfilter(api_connection,commodities, parameters)
        if json_res is None:
            return None
        tmp=json_res['results']
        if isinstance(tmp,str):
            tmp=json.loads(tmp)
        df = pd.DataFrame(data=tmp)
        return df
    @staticmethod
    def get_tradingbook_by_pk(api_connection, pk):
        """Loads tradingbooks from key

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param pk: personal key of tradingbook
        :type pk: str, required
        """
        logger.info("Fetching trading books")
        json_res = api_connection.exec_get_url('/api/portfoliomanager/tradingbooks/' + str(pk) + "/")
        for r in json_res:
            if r['pk']==pk:
                return r
        return None

    @staticmethod
    def get_tradingbook_url(api_connection, tradingbook_pk):
        """Fetches url for tradingbook from pk

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param tradingbook_pk: personal key of tradingbook
        :type tradingbook_pk: str, required
        """
        return api_connection.get_base_url() + '/api/portfoliomanager/tradingbooks/' + str(tradingbook_pk) + "/"

    @staticmethod
    def register_tradingbooks(api_connection, tradingbooks):
        """Registers tradingbooks

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param tradingbooks: list of tradingbooks
        :type tradingbooks: str, required
        """
        logger.info("Registering " + str(len(tradingbooks) )+ " tadingbooks")
        for book in tradingbooks:
            payload=book.get_dict()
            success, json_res, status_code, error_msg=api_connection.exec_post_url('/api/portfoliomanager/tradingbooks/', payload)
            if json_res is None:
                logger.error("Problems registering asset "  + book.description)
            else:
                logger.info("Asset registered " + book.description)