import requests
import json
import logging
import pandas as pd


logger = logging.getLogger(__name__)
#  Change

fields = ['pk', 'description', 'asset', 'manager', 'commodity_types', 'contract_types', 'traders']
class TradingBook():
    def __init__(self):
        self.pk=0
        self.description=None
        self.asset=None
        self.manager=None
        self.commodity_type=None
        self.contract_types=None
        self.commodity_types=[]
        self.trades=[]
    def get_dict(self):
        dict = {}
        dict['pk']=self.pk
        if self.description is not None: dict['description'] = self.description
        if self.asset is not None: dict['asset'] = self.asset
        if self.manager is not None: dict['manager'] = self.manager
        if self.commodity_type is not None: dict['commodity_type'] = self.commodity_type
        if self.contract_types is not None: dict['contract_types'] = self.contract_types
        if self.commodity_types is not None: dict['commodity_types'] = self.commodity_types
        if self.trades is not None: dict['trades'] = self.trades
        return dict

class TradingBooksApi:
    """Description...

      """

    @staticmethod
    def fetch_tradingbooks(api_connection):
        logger.info("Fetching trading books")
        json_res = api_connection.exec_get_url('/api/portfoliomanager/tradingbook/')
        print(json_res)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def load_tradingbook_by_pk(api_connection, pk):
        logger.info("Fetching trading books")
        json_res = api_connection.exec_get_url('/api/portfoliomanager/tradingbook/')
        for r in json_res:
            if r['pk']==pk:
                return r
        return None

    @staticmethod
    def register_tradingbooks(api_connection, tradingbooks):
        """ Registers assets

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param asset_list: list of assets
        :type asset_list: str, required
        """
        logger.info("Registering " + str(len(tradingbooks) )+ " tadingbooks")
        for book in tradingbooks:
            payload=book.get_dict()
            json_res=api_connection.exec_post_url('/api/portfoliomanager/tradingbook/', payload)
            if json_res is None:
                logger.error("Problems registering asset "  + book.description)
            else:
                logger.info("Asset registered " + book.description)