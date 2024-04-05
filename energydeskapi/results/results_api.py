import logging
from energydeskapi.sdk.common_utils import check_fix_date2str
from energydeskapi.profiles.profiles import GenericProfile
logger = logging.getLogger(__name__)



class ResultCalcParams:
    """ Class for  profiles
    """

    def __init__(self,
                 portfolios,
                 trading_date,
                 resolution,
                 currency):
        self.portfolios=portfolios
        self.trading_date=trading_date
        self.resolution=resolution
        self.currency=currency

    def get_dict(self, api_conn):
        dict = {}
        dict['portfolios'] = self.portfolios
        dict['trading_date'] = self.trading_date.strftime("%Y-%m-%d")
        dict['resolution'] = self.resolution
        dict['currency'] = self.currency
        return dict

class ResultsApi:
    """Class for profile management

    """

    @staticmethod
    def get_stored_results(api_connection, parameters={}):
        """Fetches credit ratings for counterparts

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/results/queryresults/', parameters)
        if json_res is not None:
            return json_res
        return None


    @staticmethod
    def calculate_results(api_connection, results_params):
        """Fetches credit ratings for counterparts

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        success, returned_data, status_code, error_msg = api_connection.exec_post_url('/api/results/calcresults/',results_params.get_dict(api_connection))
        return success, returned_data, status_code, error_msg
