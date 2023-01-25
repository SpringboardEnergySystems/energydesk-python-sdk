import logging
from energydeskapi.sdk.common_utils import check_fix_date2str
logger = logging.getLogger(__name__)



class VolumeProfile:
    """ Class for  profiles
    """

    def __init__(self,
                 description=None,
                 profile=None):
        self.pk=0
        self.description=description
        self.profile=profile

    def get_dict(self, api_conn):
        dict = {}
        prod = {}
        prod['pk'] = self.pk
        prod['description'] = self.description
        prod['profile'] = self.profile
        return prod
class ProfilesApi:
    """Class for profile management

    """

    @staticmethod
    def get_spot_profiles(api_connection, parameters={}):
        """Fetches credit ratings for counterparts

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching spot profiles")
        json_res = api_connection.exec_get_url('/api/profilemanager/spotprofiles/', parameters)
        if json_res is not None:
            return json_res
        return None

    @staticmethod
    def get_volume_profiles(api_connection, parameters={}):
        """Fetches credit ratings for counterparts

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching volume profiles")
        json_res = api_connection.exec_get_url('/api/profilemanager/volumeprofiles/', parameters)
        if json_res is not None:
            return json_res
        return None

    @staticmethod
    def upsert_volume_profile(api_connection, volume_profile):
        """Fetches credit ratings for counterparts

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        success, returned_data, status_code, error_msg = api_connection.exec_post_url('/api/profilemanager/volumeprofiles/',volume_profile.get_dict(api_connection))
        return success, returned_data, status_code, error_msg