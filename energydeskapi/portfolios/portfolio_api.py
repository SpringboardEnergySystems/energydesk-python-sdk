import json
import logging
import pandas as pd


logger = logging.getLogger(__name__)
#  Change

class PortfolioNode:
    def __init__(self):
        self.pk=0
        self.description=""
        self.trading_books=[]
        self.percentage=1
        self.manager=None
        self.assets=[]
        self.stakeholders = []
        self.sub_portfolios=[]
        self.parent_id=0
        self.parent_name = None

    def __str__(self):
        chs=""
        for c in self.sub_portfolios:
          chs+=str(c)
        return str(self.pk) + " " + self.description + " Children " + chs

    def get_dict(self, api_conn):
        dict = {}
        dict['pk'] = self.pk
        dict['description'] = self.description
        dict['trading_books']=self.trading_books
        dict['manager'] = self.manager
        #dict['percentage']=self.percentage
        dict['assets'] = self.assets
        dict['sub_portfolios'] = self.sub_portfolios
        dict['stakeholders'] = self.stakeholders
        if self.parent_id>0:
            dict['parent_portfolio'] = PortfoliosApi.get_portfolio_url(api_conn, self.parent_id)
        return dict

class PortfoliosApi:
    """Class for portfolios

      """

    @staticmethod
    def get_portfolios(api_connection, parameters={}):
        """Fetches all portfolios

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching portfolios")
        json_res = api_connection.exec_get_url('/api/portfoliomanager/portfolios/', parameters)
        if json_res is None:
            return None
        return json_res
    @staticmethod

    def get_portfolios_embedded(api_connection, parameters={}):
        """Fetches all portfolios

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching portfolios (embedded) ")
        json_res = api_connection.exec_get_url('/api/portfoliomanager/portfolios/embedded/', parameters)
        if json_res is None:
            return None
        return json_res


    @staticmethod
    def get_portfolio_by_pk(api_connection, pk):
        """Loads portfolios from key

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param pk: personal key of portfolio
        :type pk: str, required
        """
        logger.info("Fetching portfolio " + str(pk))
        dict = api_connection.exec_get_url('/api/portfoliomanager/portfolios/' + str(pk) + "/")
        return dict

    @staticmethod
    def get_portfolio_url(api_connection, portfolio_pk):
        """Fetches url for portfolio from pk

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param tradingbook_pk: personal key of tradingbook
        :type tradingbook_pk: str, required
        """
        return api_connection.get_base_url() + '/api/portfoliomanager/portfolios/' + str(portfolio_pk) + "/"


    @staticmethod
    def upsert_portfolio(api_connection, portfolio):
        """Insefrts or updates a tradingbook

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param tradingbooks: list of tradingbooks
        :type tradingbooks: str, required
        """
        logger.info("Updating a tradingbook")
        payload=portfolio.get_dict(api_connection)
        if portfolio.pk>0:
            success, json_res, status_code, error_msg=api_connection.exec_patch_url('/api/portfoliomanager/portfolios/' + str(portfolio.pk) + "/", payload)
        else:
            success, json_res, status_code, error_msg=api_connection.exec_post_url('/api/portfoliomanager/portfolios/', payload)
        if json_res is None:
            logger.error("Problems saving portfolio "  + str(portfolio.description))
        else:
            logger.info("Portfolio updated " + str(portfolio.description))
