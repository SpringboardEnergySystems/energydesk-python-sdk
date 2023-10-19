import logging
import pandas as pd
#from energydeskapi.sdk.common_utils import parse_enum_type
import json
logger = logging.getLogger(__name__)

class AnnualAccountsApi:
    """Class for rating API wrapper

    """

    @staticmethod
    def update_annual_accounts(api_connection, company, payload):
        """Updates crea

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param user: object of user
        :type user: str, required
        """
        #If company[0] is zero, we should send a POST command in stead; and/or use a different function for it
        success, json_res, status_code, error_msg = api_connection.exec_patch_url('/api/creditrisk/companyaccounts/' + company + '/', payload)
        if json_res is None:
            logger.error("Problems updating rating for comnpany " + str(company))
            return False
        else:
            logger.info("Updated company")
            return True

    @staticmethod
    def get_annual_accounts(api_connection):
        """Fetching list of companies

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching rated companies")
        json_res=api_connection.exec_get_url('/api/creditrating/companyaccounts/')
        if json_res is not None:
            return json_res
        return None

    @staticmethod
    def get_annual_accounts_of_company(api_connection, company_pk):
        """Fetches rated company

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching rated companny with key " + str(company_pk))
        json_res=api_connection.exec_get_url('/api/creditrisk/companyaccounts/' + str(company_pk) + "/")
        if json_res is not None:
            return json_res
        return None
    
    @staticmethod
    def post_annual_accounts(api_connection, payload):
        logger.info("Fetching company with id " + str(id))
        json_res=api_connection.exec_post_url('/api/creditrisk/companyaccounts/', payload)
        if json_res is not None:
            return json_res
        return None
    
    def post_manual_annual_accounts(api_connection, payload):
        logger.info("Fetching company with id " + str(id))
        json_res=api_connection.exec_post_url('/api/creditrisk/manualinput/', payload)
        if json_res is not None:
            return json_res
        return None

class RatingApi:
    """Class for rating API wrapper

    """
    #
    @staticmethod
    def update_rating(api_connection, rating_pk, payload):
        """Updates crea

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param user: object of user
        :type user: str, required
        """
        #If rating[0] is zero, we should send a POST command in stead; and/or use a different function for it
        success, json_res, status_code, error_msg = api_connection.exec_patch_url('/api/creditrating/ratings/' + str(rating_pk) + '/', payload)
        if json_res is None:
            logger.error("Problems updating rating for comnpany " + str(rating_pk))
            return False
        else:
            logger.info("Updated rating")
            return True

    @staticmethod
    def get_ratings(api_connection):
        """Fetching list of companies

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching rated companies")
        json_res=api_connection.exec_get_url('/api/creditrisk/ratings/')
        if json_res is not None:
            return json_res
        return None

    @staticmethod
    def get_rating_from_company_pk(api_connection, company_pk):
        logger.info("Fetching rated companny with key " + str(company_pk))
        json_res=api_connection.exec_get_url('/api/creditrisk/ratings/', parameters={'company__id': str(company_pk)})
        if json_res is not None:
            return json_res
        return None

    @staticmethod
    def get_rating(api_connection, pk):
        """Fetches rated rating

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching rated companny with key " + str(pk))
        json_res=api_connection.exec_get_url('/api/creditrating/ratings/' + str(pk) + "/")
        if json_res is not None:
            return json_res
        return None
    
    @staticmethod
    def get_embedded_rating(api_connection, pk):
        """Fetches rated rating

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching rated companny with key " + str(pk))
        json_res=api_connection.exec_get_url('/api/creditrisk/ratings/' + str(pk) + "/")
        if json_res is not None:
            return json_res
        return None

    @staticmethod
    def post_calculate_rating(api_connection, payload):
        logger.info("Calculating rating")
        json_res=api_connection.exec_post_url_nojson('/api/creditrisk/calculaterating/', payload)
        if json_res is not None:
            return json_res
        return None
