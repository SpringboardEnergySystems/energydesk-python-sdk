import requests
import json
import logging
import pandas as pd
from energydeskapi.customers.customers_api import CustomersApi

logger = logging.getLogger(__name__)
#  Change
class ElvizLinksApi:
    """Description...

      """

    @staticmethod
    def get_treasury_banks(api_connection):
        logger.info("Fetching treasury bank list")
        json_res = api_connection.exec_get_url('/api/treasury/treasurybanks/')
        print(json_res)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def lookup_company_mapping(api_connection, elviz_company_id):
        logger.info("Looking up company mappings")
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


