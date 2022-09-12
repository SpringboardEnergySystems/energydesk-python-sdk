import requests
import json
import logging
import pandas as pd
from energydeskapi.customers.customer_api import CustomerApi

logger = logging.getLogger(__name__)
#  Change
class TreasuryApi:
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
    def register_treasury_bank(api_connection, registry_number, treasury_system_name):
        logger.info("Fetching treasury bank list")
        company=CustomerApi.get_company_from_registry_number( api_connection,registry_number)
        print(company)
        comp_url=api_connection.get_base_url() + "/api/customers/company/" + str(company['pk']) + "/"
        print(comp_url)
        payload={"treasury_system_name":treasury_system_name,
                 "internal_company": comp_url}
        json_res = api_connection.exec_post_url('/api/treasury/treasurybanks/',payload)
        print(json_res)

        return True


