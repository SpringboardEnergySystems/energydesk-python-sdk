import json
import logging
import pandas as pd
import json
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
        if self.geom is not None:
            dict['geom'] = json.dumps(self.geom)
        if self.location_type is not None: dict['location_type'] = LocationApi.get_location_type_url(api_conn,parse_enum_type(self.location_type))
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
    def get_default_zones(api_connection):
        """Fetches main area of company

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching default zones")
        json_res=api_connection.exec_get_url('/api/locations/default-zones/')
        if json_res is not None:
            return json_res
        return None
    @staticmethod
    def get_dso_area(api_connection, dso_name):
        """Fetches main area of company

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching DSO area {}".format(dso_name))
        json_res=api_connection.exec_get_url('/api/locations/dsomap/?dso_name=' + dso_name)
        if json_res is not None:
            return json_res
        return None

    @staticmethod
    def generate_asset_polygon(api_connection, asset_list):
        """Fetches main area of company

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        parameters={
            'assets_pk__in':asset_list
        }
        json_res=api_connection.exec_get_url('/api/locations/createassetpolygon/',parameters)
        if json_res is not None:
            return json_res
        return None

    @staticmethod
    def generate_default_map(api_connection, map_type, include_assets, zones=[], country="NOR"):
        """Fetches main area of company
        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Generate default geojson")

        payload={
            "map_type":map_type,
            "add_bidding_zones": zones,
            "show_assets":include_assets,
            "country":country
        }

        success, json_res, status_code, error_msg=api_connection.exec_post_url('/api/locations/generate-default-map/', payload)
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
                success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/locations/localareas/', loc.get_dict(api_connection))
            else:
                success, json_res, status_code, error_msg = api_connection.exec_patch_url('/api/locations/localareas/' + str(loc.pk) + "/", loc.get_dict(api_connection))
            if success==False:
                print(error_msg)
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
    def get_local_areas(api_connection, parameters={}):
        """Fetches local area from location type pk

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param location_type_enum: type of location
        :type location_type_enum: str
        """

        json_res=api_connection.exec_get_url('/api/locations/localareas/',parameters)
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
