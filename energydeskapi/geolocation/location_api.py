import requests
import json
import logging
import pandas as pd
logger = logging.getLogger(__name__)

class LocalArea:
    def __init__(self):
         self.pk=0,
         self.title=None,
         self.description=None
         self.area_type=None
    def get_dict(self, api_conn):
        dict = {}
        dict['pk'] = self.pk
        if self.title is not None: dict['title'] = self.title
        if self.area_type is not None: dict['area_type'] = LocationApi.get_location_type_url(api_conn,self.area_type)
        if self.description is not None: dict['description'] = self.description
        return dict

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
    def get_location_type_url(api_connection, location_type_enum):
        type_pk = location_type_enum if isinstance(location_type_enum, int) else location_type_enum.value
        return api_connection.get_base_url() + '/api/locations/locationtypes/' + str(
            type_pk) + "/"

    @staticmethod
    def upsert_local_areas(api_connection, local_areas):
        """Upsert local area
        Inserts (new) or updated existing local area
        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        for loc in local_areas:
            if loc.pk==0:
                json_res = api_connection.exec_post_url('/api/locations/localareas/', loc.get_dict(api_connection))
            else:
                json_res = api_connection.exec_patch_url('/api/locations/localareas/' + str(loc.pk) + "/", loc.get_dict(api_connection))
            print(json_res)

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

    @staticmethod
    def get_location_types(api_connection):

        """Fetches local area

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching geolocatioin")
        json_res=api_connection.exec_get_url('/api/locations/locationtypes/')
        if json_res is not None:
            return json_res
        return None


    @staticmethod
    def get_location_types_df(api_connection):
        json_res=LocationApi.get_location_types(api_connection)
        return None if json_res is None else pd.DataFrame(data=json_res)

    @staticmethod
    def get_geolocation_details(api_connection, locarea_pk):

        """Fetches local area

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching geolocatioin")
        json_res=api_connection.exec_get_url('/api/locations/geolocation-details/' + str(locarea_pk) + "/")
        if json_res is not None:
            return json_res
        return None
