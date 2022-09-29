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
        json_res=api_connection.exec_get_url('/api/locations/mainareas/')
        if json_res is not None:
            return json_res
        return None

    @staticmethod
    def get_local_areas(api_connection, location_type_enum):
        type_pk = location_type_enum if isinstance(location_type_enum, int) else location_type_enum.value
        """Fetches local area

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching local area geojson")
        json_res=api_connection.exec_get_url('/api/locations/localareas/?location_type=' + str(type_pk))
        if json_res is not None:
            return json_res
        return None


