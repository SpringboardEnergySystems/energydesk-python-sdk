import requests
import json
import logging
import pandas as pd
from energydeskapi.customers.customers_api import CustomersApi

logger = logging.getLogger(__name__)
#  Change
class TreasuryApi:
    """Class for treasury banks

    """

    @staticmethod
    def get_treasury_banks(api_connection):
        """Fetches all treasury banks

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching treasury bank list")
        json_res = api_connection.exec_get_url('/api/treasury/treasurybanks/')
        print(json_res)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def register_treasury_bank(api_connection, registry_number, treasury_system_name):
        """Registers treasury bank from brreg

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param registry_number: registry number of a company from brreg
        :type registry_number: str, required
        :param treasury_system_name: name of a treasury system
        :type treasury_system_name: str, required
        """
        logger.info("Fetching treasury bank list")
        company=CustomersApi.get_company_from_registry_number( api_connection,registry_number)
        print(company)
        comp_url=api_connection.get_base_url() + "/api/customers/companies/" + str(company['pk']) + "/"
        print(comp_url)
        payload={"treasury_system_name":treasury_system_name,
                 "internal_company": comp_url}
        json_res = api_connection.exec_post_url('/api/treasury/treasurybanks/',payload)
        print(json_res)

        return True


