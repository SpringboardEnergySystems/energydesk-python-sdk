import requests
import json
import logging
import pandas as pd
logger = logging.getLogger(__name__)


class CustomerApi:
    """Class for user profiles and companies

    """
    @staticmethod
    def get_user_profile(api_connection):
        """Fetches user profile

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching user profile")
        json_res=api_connection.exec_get_url('/api/energydesk/getuserprofile/')
        if json_res is not None:
            return json_res
        return None

    @staticmethod
    def get_users(api_connection):
        """Fetches user profile

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching user profile")
        json_res=api_connection.exec_get_url('/api/customers/users/traders')
        if json_res is not None:
            df = pd.DataFrame(data=json_res)
            return df
        return None

    def register_company(api_connection, company):
        json_res = api_connection.exec_post_url('/api/customers/register_company', company)
        if json_res is None:
            return False
        print(json_res)
        return json_res["Registration"]

    @staticmethod
    def get_company_types_df(api_connection):
        """Fetches all company types in system with basic key+ name infmation

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching company types")
        json_res=api_connection.exec_get_url('/api/customers/companytype/')
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def get_companies_ext_df(api_connection):
        """Fetches all companies in system with basic key+ name infmation

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching companylist")
        json_res=api_connection.exec_get_url('/api/customers/get_all_companies')
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res["companies"])
        return df

    @staticmethod
    def get_company_by_name(api_connection, company_name):
        df = CustomerApi.get_companies_ext_df(api_connection)
        dfres = df.loc[df['company_name'] == company_name]
        if len(dfres.index)==0:
            logger.warning("No company named " + str(company_name))
            return None
        comppk = dfres['pk'].values[-1]
        return comppk


    @staticmethod
    def get_companies(api_connection):
        """Fetches all company objects with URL relations. Will only return companies for which the user has rights

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching company list")
        json_res=api_connection.exec_get_url('/api/customers/company')
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_company_from_registry_number(api_connection, registry_number):
        """Fetches all company objects with URL relations. Will only return companies for which the user has rights

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching company " + str(registry_number))
        json_res=api_connection.exec_get_url('/api/customers/company_from_registry_number?registry_number=' + registry_number )
        if json_res is None:
            return None
        return json_res