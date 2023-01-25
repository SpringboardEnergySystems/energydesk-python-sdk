import logging
from energydeskapi.sdk.common_utils import check_fix_date2str
logger = logging.getLogger(__name__)

class ProfilesApi:
    """Class for profile management

    """
    @staticmethod
    def get_volume_profiles(api_connection, parameters={}):
        """Fetches credit ratings for counterparts

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching volume profiles")
        json_res = api_connection.exec_get_url('/api/markets/query-custom-profiles/', parameters)
        if json_res is not None:
            return json_res
        return None