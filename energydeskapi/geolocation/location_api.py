import requests
import json
import logging
import pandas as pd
from energydeskapi.sdk.common_utils import parse_enum_type
logger = logging.getLogger(__name__)

class LocalArea:
    def __init__(self):
         self.pk=0,
         self.title=None,
         self.description=None
         self.location_type=None
         self.geom=None
         self.is_main_area=True
    def get_dict(self, api_conn):
        dict = {}
        dict['pk'] = self.pk
        if self.title is not None: dict['title'] = self.title
        if self.geom is not None: dict['geom'] = self.geom
        if self.location_type is not None: dict['location_type'] = LocationApi.get_location_type_url(parse_enum_type(api_conn,self.location_type))
        if self.description is not None: dict['description'] = self.description
        if self.is_main_area is not None: dict['is_main_area'] = self.is_main_area
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
    def generate_default_map(api_connection, map_type="COUNTRY", param="NOR"):
        """Fetches main area of company
        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Generate default geojson")
        payload={
            "map_type":map_type,
            "param":param
        }
        json_res=api_connection.exec_post_url('/api/locations/generate-default-map/', payload)
        if json_res is not None:
            return json_res
        return None

    @staticmethod
    def get_location_type_url(api_connection, location_type_enum):
        """Fetches url for location type from pk

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param location_type_enum: type of location
        :type location_type_enum: str, required
        """
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
            if int(loc.pk)==0:
                json_res = api_connection.exec_post_url('/api/locations/localareas/', loc.get_dict(api_connection))
            else:
                json_res = api_connection.exec_patch_url('/api/locations/localareas/' + str(loc.pk) + "/", loc.get_dict(api_connection))
            return json_res

    @staticmethod
    def get_local_area_url(api_connection, key):
        """Fetches url for location type from pk

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param key: personal key
        :type key: str, required
        """
        return api_connection.get_base_url() + '/api/locations/localareas/' + str(
            key) + "/"

    @staticmethod
    def get_local_areas(api_connection, location_type_enum):
        """Fetches local area from location type pk

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param location_type_enum: type of location
        :type location_type_enum: str
        """
        type_pk = location_type_enum if isinstance(location_type_enum, int) else location_type_enum.value
        logger.info("Fetching local area geojson")
        json_res=api_connection.exec_get_url('/api/locations/localareas/?location_type=' + str(type_pk))
        if json_res is not None:
            return json_res
        return None



    def get_local_areas_df(api_connection,  location_type_enum):
        """Fetches local areas and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param location_type_enum: type of location
        :type location_type_enum: str
        """
        json_res=LocationApi.get_local_areas(api_connection, location_type_enum)
        return None if json_res is None else pd.DataFrame(data=json_res)

    @staticmethod
    def get_location_types(api_connection):
        """Fetches all location types

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
        """Fetches all location types and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res=LocationApi.get_location_types(api_connection)
        return None if json_res is None else pd.DataFrame(data=json_res)

    @staticmethod
    def get_geolocation_details(api_connection, locarea_pk):
        """Fetches location details from pk

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param locarea_pk: personal key of location
        :type locarea_pk: str, required
        """
        logger.info("Fetching geolocatioin")
        json_res=api_connection.exec_get_url('/api/locations/geolocation-details/' + str(locarea_pk) + "/")
        if json_res is not None:
            return json_res
        return None
