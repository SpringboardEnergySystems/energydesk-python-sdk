import logging
from energydeskapi.sdk.common_utils import check_fix_date2str
from energydeskapi.profiles.profiles import GenericProfile
logger = logging.getLogger(__name__)



class StoredProfile:
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
    def get_volume_profile_by_key(api_connection, key):
        """Fetches url for location type from pk

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param key: personal key
        :type key: str, required
        """
        res=ProfilesApi.get_volume_profiles(api_connection, {'page_size':100})
        if res is None:
            return None
        for r in res['results']:
            if r['pk']==key:
                return r
        return None


    @staticmethod
    def upsert_volume_profile(api_connection, profile):
        """Fetches credit ratings for counterparts

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        success, returned_data, status_code, error_msg = api_connection.exec_post_url('/api/profilemanager/volumeprofiles/',profile.get_dict(api_connection))
        return success, returned_data, status_code, error_msg

    @staticmethod
    def upsert_yearlyfactors(api_connection, factor):
        """Registers yearly factors

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        success, returned_data, status_code, error_msg = api_connection.exec_post_url(
            '/api/profilemanager/yearhourlyfactorprofile/', factor)
        return success, returned_data, status_code, error_msg

    @staticmethod
    def convert_volumeprofile_to_factors(api_connection, volume_profile:GenericProfile):
        """Fetches credit ratings for counterparts

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Converting volume profiles to factors")
        payload={
            'profile':volume_profile.to_dict()
        }
        success, returned_data, status_code, error_msg  = api_connection.exec_post_url('/api/profilemanager/convertvolume2factors/', payload)
        return success, returned_data, status_code, error_msg

    @staticmethod
    def convert_relativeprofile_to_yearlyfactors(api_connection, year_start, year_count, relative_profile:GenericProfile):
        """Fetches credit ratings for counterparts

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Converting relative profile to factors")
        payload={
            'year_start':year_start,
            'year_count':year_count,
            'relative_profile':relative_profile.to_dict()
        }
        success, returned_data, status_code, error_msg  = api_connection.exec_post_url('/api/profilemanager/convertvolume2yearlyprofile/', payload)
        return success, returned_data, status_code, error_msg
