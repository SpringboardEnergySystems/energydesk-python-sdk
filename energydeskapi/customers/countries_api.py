import logging
import pandas as pd
logger = logging.getLogger(__name__)


class CountriesApi:
    """Class for user profiles and companies

    """
    @staticmethod
    def get_countries(api_connection, parameters={}):
        """Fetches all companies

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res=api_connection.exec_get_url('/api/customers/countries/', parameters)
        if json_res is None:
            return None
        return json_res
