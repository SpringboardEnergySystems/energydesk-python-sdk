import requests
import json
import logging
import pandas as pd
from energydeskapi.customers.customers_api import CustomersApi
from energydeskapi.customers.users_api import UsersApi
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
                   "elviz_userr_name": elviz_userr_name,
                   "enegydesk_username": profile_url}
        existing = ElvizLinksApi.lookup_user_mapping(api_connection, enegydesk_username)
        if existing is None:
            json_res = api_connection.exec_post_url('/api/elvizmapping/users/', payload)
        else:
            json_res = api_connection.exec_patch_url('/api/elvizmapping/users/'
                                                     + str(existing['pk']) + "/", payload)
        print(json_res)
        return True


