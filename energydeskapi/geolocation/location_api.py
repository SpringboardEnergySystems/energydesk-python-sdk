import requests
import json
import logging
import pandas as pd
logger = logging.getLogger(__name__)


class LocationApi:
    """Class for user profiles and companies

    """
    @staticmethod
    def get_main_production_area(api_connection):
        """Fetches main area of company

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching main area geojson")
        json_res=api_connection.exec_get_url('/api/location/getmainarea/')
        if json_res is not None:
            return json_res
        return None
