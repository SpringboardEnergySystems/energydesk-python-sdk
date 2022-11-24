import logging
import pandas as pd
logger = logging.getLogger(__name__)

#fields = ['pk', 'asset_id', 'extern_asset_id', 'description', 'asset_type', 'grid_connection', 'power_supplier',
 #         'asset_owner', 'asset_manager', 'meter_id', 'sub_meter_id', 'vendor', 'is_active']


class Asset:
    def __init__(self):
        self.pk=0
        self.asset_id=None
        self.extern_asset_id=None
        self.description=""
        self.asset_type=None
        self.grid_company=None
        self.power_supplier=None
        self.asset_owner=None
        self.asset_manager=None
        self.price_area= None
        self.meter_id=""
        self.sub_meter_id=""
        self.vendor=None
        self.is_main_meter=True
        self.location="0,0"
        self.is_active=True

    def get_dict(self):
        dict = {}
        dict['pk']=self.pk
        if self.asset_id is not None: dict['asset_id'] = self.asset_id
        if self.extern_asset_id is not None: dict['extern_asset_id'] = self.extern_asset_id
        if self.description is not None: dict['description'] = self.description
        if self.asset_type is not None: dict['asset_type'] = self.asset_type
        if self.grid_company is not None: dict['grid_connection'] = self.grid_company
        if self.power_supplier is not None: dict['power_supplier'] = self.power_supplier
        if self.asset_owner is not None: dict['asset_owner'] = self.asset_owner
        if self.asset_manager is not None: dict['asset_manager'] = self.asset_manager
        if self.meter_id is not None: dict['meter_id'] = self.meter_id
        if self.sub_meter_id is not None: dict['sub_meter_id'] = self.sub_meter_id
        if self.vendor is not None: dict['vendor'] = self.vendor
        if self.is_main_meter is not None: dict['is_main_meter'] = self.is_main_meter
        if self.is_active is not None: dict['is_active'] = self.is_active
        if self.price_area is not None: dict['price_area'] = self.price_area
        if self.location is not None: dict['location'] = self.location
        return dict


class AssetsApi:
    """ Class for assets

    """

    @staticmethod
    def get_asset_type_url(api_connection, asset_type_enum):
        """Fetches asset type from url

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param asset_type_enum: type of asset
        :type asset_type_enum: str, required
        """
        atype_pk = asset_type_enum if isinstance(asset_type_enum, int) else asset_type_enum.value
        return api_connection.get_base_url() + '/api/assets/assettypes/' + str(atype_pk) + "/"

    @staticmethod
    def get_asset_type(api_connection, asset_type_enum):
        """Fetches asset type from url

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param asset_type_enum: type of asset
        :type asset_type_enum: str, required
        """
        atype_pk = asset_type_enum if isinstance(asset_type_enum, int) else asset_type_enum.value
        json_res = api_connection.exec_get_url('/api/assets/assettypes/' + str(asset_type_enum)) + "/"
        if json_res is None:
            return None
        return json_res

    # This function returns a single price (avg) for the period requested
    @staticmethod
    def create_assets(api_connection, asset_list):
        """Registers assets

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param asset_list: list of assets
        :type asset_list: str, required
        """
        logger.info("Registering " + str(len(asset_list) )+ " assets")
        for asset in asset_list:
            payload=asset.get_dict()
            success, json_res, status_code, error_msg=api_connection.exec_post_url('/api/assets/assets/', payload)
            if json_res is None:
                logger.error("Problems registering asset "  + asset.description)
            else:
                logger.info("Asset registered " + asset.description)

    @staticmethod
    def get_asset_types(api_connection):
        """Fetches the type of all assets

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/assets/assettypes/')
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def get_asset_url(api_connection, asset_pk):
        """Fetches asset from url

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param asset_pk: personal key of asset
        :type asset_pk: str, required
        """
        return api_connection.get_base_url() + '/api/assets/assets/' + str(asset_pk) + "/"

    @staticmethod
    def get_assets(api_connection, parameters={}):
        """Fetches all assets

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/assets/assets/', parameters)
        if json_res is None:
            return None
        return json_res
        # json_res = api_connection.exec_get_url('/api/assets/assets/')
        # if json_res is None:
        #     return None
        # return json_res

    @staticmethod
    def get_assets_embedded(api_connection, parameters={}):
        """Fetches all assets with extended information

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/assets/assets/embedded', parameters)
        return json_res

    @staticmethod
    def get_assets_df(api_connection, parameters={}):
        """Fetches all assets with extended information

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        parameters['page_size']=200
        json_res = api_connection.exec_get_url('/api/assets/assets/embedded', parameters)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res['results'])
        return df

    @staticmethod
    def get_asset_by_description(api_connection, description):
        """Fetches assets from description

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param description: description of asset
        :type description: str, required
        """
        logger.info("Fetching assets with description " + str(description))
        success, json_res, status_code, error_msg=api_connection.exec_post_url('/api/assets/assets-by-filter/', {'description':description})
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_asset_by_key(api_connection, pk):
        """Fetches asset from key

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param pk: personal key of asset
        :type pk: str, required
        """
        logger.info("Fetching assets with key " + str(pk))
        json_res=api_connection.exec_get_url('/api/assets/assets/' + str(pk) + "/")
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_assetsbytype_ext(api_connection, asset_type_enum):
        """Fetches assets from types with extended information

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param asset_type_enum: type of asset
        :type asset_type_enum: str, required
        """
        payload={"asset_type_enum": str(asset_type_enum.value)}
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/assets/assets-by-type-extended/', payload)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df
