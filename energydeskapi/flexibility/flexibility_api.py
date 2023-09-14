import logging
import pandas as pd
logger = logging.getLogger(__name__)

class FlexibilityApi:
    """ Class for flexibility

    """

    @staticmethod
    def get_empty_dispatch_schedule(api_connection):
        """Fetches empty schedule

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param asset_type_enum: type of asset
        :type asset_type_enum: str, required
        """
        json_res = api_connection.exec_get_url('/api/flexiblepower/generateemptyschedule/')
        if json_res is None:
            return None
        return json_res
