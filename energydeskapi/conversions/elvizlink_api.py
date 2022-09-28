import requests
import json
import logging
import pandas as pd
from energydeskapi.customers.customers_api import CustomersApi
from energydeskapi.customers.users_api import UsersApi
from energydeskapi.portfolios.tradingbooks_api import TradingBooksApi
logger = logging.getLogger(__name__)
#  Change
class ElvizLinksApi:
    """Description...

      """
    @staticmethod
    def get_company_mappings(api_connection):
        logger.info("Looking up company mappings")
        return api_connection.exec_get_url('/api/elvizmapping/companies/')

    @staticmethod
    def lookup_company_mapping(api_connection, elviz_company_id):
        logger.info("Looking up company mapping with id " + str(elviz_company_id))
        json_res = api_connection.exec_get_url('/api/elvizmapping/companies/')
        for comp in json_res:
            if comp['elviz_company_id']==elviz_company_id:
                print("Found company ", comp)
                return comp
        return None
    @staticmethod
    def upsert_company_mapping(api_connection, registry_number, elviz_company_id, elviz_company_name):
        logger.info("Register or update company mappingrs")
        company=CustomersApi.get_company_from_registry_number( api_connection,registry_number)
        if company is None:
            logger.error("Cannot map a company that is not stored internally with registry " + str(registry_number))
            return False

        comp_url=api_connection.get_base_url() + "/api/customers/companies/" + str(company['pk']) + "/"
        payload={"elviz_company_id":elviz_company_id,
                 "elviz_company_name": elviz_company_name,
                 "energydesk_company":comp_url}
        print("Updating " + str(payload))
        existing=ElvizLinksApi.lookup_company_mapping(api_connection, elviz_company_id)
        if existing is None:
            json_res = api_connection.exec_post_url('/api/elvizmapping/companies/',payload)
        else:
            json_res = api_connection.exec_patch_url('/api/elvizmapping/companies/'
                                                     + str(existing['pk']) + "/", payload)
        print(json_res)
        return True

    @staticmethod
    def get_user_mappings(api_connection):
        logger.info("Looking up user mappings")
        return api_connection.exec_get_url('/api/elvizmapping/users/')

    @staticmethod
    def lookup_user_mapping(api_connection, elviz_user_id):
        logger.info("Looking up users mapping with id " + str(elviz_user_id))
        json_res = api_connection.exec_get_url('/api/elvizmapping/users/')
        for comp in json_res:
            if comp['elviz_user_id'] == elviz_user_id:
                print("Found user ", comp)
                return comp
        return None

    @staticmethod
    def upsert_user_mapping(api_connection, enegydesk_username, elviz_user_id, elviz_userr_name):
        logger.info("Register or update user mapping")
        edeskuser = UsersApi.get_profile_by_username(api_connection, enegydesk_username)
        if edeskuser is None:
            logger.error("Cannot map a user that is not stored internally with name " + str(enegydesk_username))
            return False

        profile_url = api_connection.get_base_url() + "/api/customers/profiles/" + str(edeskuser['pk']) + "/"
        payload = {"elviz_user_id": elviz_user_id,
                   "elviz_user_name": elviz_userr_name,
                   "energydesk_profile": profile_url}
        existing = ElvizLinksApi.lookup_user_mapping(api_connection, enegydesk_username)
        if existing is None:
            json_res = api_connection.exec_post_url('/api/elvizmapping/users/', payload)
        else:
            json_res = api_connection.exec_patch_url('/api/elvizmapping/users/'
                                                     + str(existing['pk']) + "/", payload)
        print(json_res)
        return True


    @staticmethod
    def get_portfolio_mappings(api_connection):
        logger.info("Looking up portfolio mappings")
        return api_connection.exec_get_url('/api/elvizmapping/portfolios/')

    @staticmethod
    def lookup_tadingbook(api_connection, tradingbook_name):
        logger.info("Looking up tradingbook " + str(tradingbook_name))
        df = TradingBooksApi.fetch_tradingbooks(api_connection)
        #print(df)
        for index,row in df.iterrows():
            if row['description'] == tradingbook_name:
                print("Found tradingbook_name ", tradingbook_name)
                return row['pk']
        print("Did not find", tradingbook_name)
        return None

    @staticmethod
    def lookup_portfolio_mapping(api_connection, elviz_portfolio_id):
        logger.info("Looking up users mapping with id " + str(elviz_portfolio_id))
        json_res = api_connection.exec_get_url('/api/elvizmapping/portfolios/')
        for comp in json_res:
            if comp['elviz_portfolio_id'] == elviz_portfolio_id:
                print("Found portfolio ", comp)
                return comp
        return None
    @staticmethod
    def upsert_portfolio_mapping(api_connection, tradingbook, elviz_portfolio_id, elviz_portfolio_name):
        logger.info("Register or update user mapping")
        edeskbook = ElvizLinksApi.lookup_tadingbook(api_connection, tradingbook)
        if edeskbook is None:
            logger.error("Cannot map a portfolio that is not stored internally with name " + str(tradingbook))
            return False

        tbook_url=TradingBooksApi.get_tradingbook_url(api_connection, edeskbook)
        payload = {"elviz_portfolio_id": elviz_portfolio_id,
                   "elviz_portfolio_name": elviz_portfolio_name,
                   "energydesk_trading_book": tbook_url}
        existing = ElvizLinksApi.lookup_portfolio_mapping(api_connection, elviz_portfolio_id)
        print(existing)
        if existing is None:
            json_res = api_connection.exec_post_url('/api/elvizmapping/portfolios/', payload)
        else:
            json_res = api_connection.exec_patch_url('/api/elvizmapping/portfolios/'
                                                     + str(existing['pk']) + "/", payload)
        print(json_res)
        return True