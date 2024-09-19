import logging
import json
from energydeskapi.assets.assets_api import AssetsApi
from energydeskapi.types.asset_enum_types import TimeSeriesTypesEnum
from energydeskapi.types.baselines_enum_types import BaselinesModelsEnums
from energydeskapi.types.contract_enum_types import QuantityTypeEnum, QuantityUnitEnum
from energydeskapi.assetdata.assetdata_api import AssetDataApi
import pendulum
from energydeskapi.assetdata.baselines_api import BaselinesApi
from energydeskapi.types.flexibility_enum_types import ExternalMarketTypeEnums
import pandas as pd
from datetime import timezone, datetime, date
import json, pendulum
from energydeskapi.contracts.contracts_api import ContractsApi
from energydeskapi.types.contract_enum_types import QuantityTypeEnum, QuantityUnitEnum
from energydeskapi.types.flexibility_enum_types import RegulationTypeEnums
from json import JSONEncoder
from dataclasses import dataclass
logger = logging.getLogger(__name__)


class ExternalMarketAsset:
    def __init__(self, flexible_asset_pk, external_market_key=ExternalMarketTypeEnums.NODES.value,
                 external_market_asset_properties=None):
        self.pk = 0
        self.flexible_asset_pk = flexible_asset_pk
        self.external_market_key=external_market_key
        self.external_market_asset_properties = external_market_asset_properties

    def get_dict(self, api_conn):
        dict = {}
        dict['pk'] = self.pk
        if self.flexible_asset_pk is not None:
            dict['flexible_asset'] = FlexibilityApi.get_asset_offer_url(api_conn, self.flexible_asset_pk)
        if self.external_market_key is not None:
            dict['external_market'] = FlexibilityApi.get_flexible_market_url(api_conn,self.external_market_key)
        if self.external_market_asset_properties is not None:
            dict['external_market_asset_properties'] = self.external_market_asset_properties
        return dict


class AssetScheduledRegulation:
    def __init__(self, flexible_asset_pk, regulation_quantity,
                 regulation_start, regulation_stop, extern_asset_id=None):
        self.pk = 0
        self.flexible_asset_pk = flexible_asset_pk
        self.extern_asset_id = extern_asset_id
        self.updated_at_time=pendulum.now(tz="Europe/Oslo").in_timezone("UTC")
        self.regulation_quantity = regulation_quantity
        # Default values. Consumption down is same as regulate up (energy)
        self.regulation_type = RegulationTypeEnums.REGULATE_UP.value
        self.quantity_type=QuantityTypeEnum.EFFECT.value
        self.quantity_unit=QuantityUnitEnum.KW.value
        self.regulation_cancelled=False
        self.regulation_start=regulation_start
        self.regulation_stop=regulation_stop

    def get_dict(self, api_conn):
        dict = {}
        dict['pk'] = self.pk
        if self.flexible_asset_pk is not None:
            dict['flexible_asset'] = FlexibilityApi.get_asset_offer_url(api_conn, self.flexible_asset_pk)
        if self.quantity_unit is not None: dict['quantity_unit'] = ContractsApi.get_quantity_unit_url(api_conn,
                                                                                                            self.quantity_unit)
        if self.quantity_type is not None: dict['quantity_type'] = ContractsApi.get_quantity_type_url(api_conn,
                                                                                                            self.quantity_type)
        if self.regulation_type is not None: dict['regulation_type'] = FlexibilityApi.get_regulation_type_url(api_conn,
                                                                                                            self.regulation_type)

        if self.regulation_cancelled is not None: dict['regulation_cancelled'] = self.regulation_cancelled
        if self.regulation_start is not None: dict['regulation_start'] = str(self.regulation_start)
        if self.regulation_stop is not None: dict['regulation_stop'] = str(self.regulation_stop)
        if self.updated_at_time is not None: dict['updated_at_time'] = str(self.updated_at_time)
        if self.regulation_quantity is not None: dict['regulation_quantity'] = self.regulation_quantity
        if self.extern_asset_id is not None: dict['extern_asset_id'] = self.extern_asset_id
        return dict


class FlexibilityApi:
    """ Class for flexibility
    """

    @staticmethod
    def get_regulation_type_url(api_connection, regulation_type_enum):
        """
        """
        type_pk = regulation_type_enum if isinstance(regulation_type_enum, int) else regulation_type_enum.value
        return api_connection.get_base_url() + '/api/flexiblepower/regulation/' + str(type_pk) + "/"

    @staticmethod
    def get_flexible_assets(api_connection, parameters={}):
        """Fetches empty schedule

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/flexiblepower/flexibleassets/embedded/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def remove_asset_flexibility(api_connection, extern_asset_id):
        asset_offering=FlexibilityApi.get_flexible_assets(api_connection, parameters={'asset__extern_asset_id':extern_asset_id})
        print(asset_offering)
        flag=True
        for off in asset_offering['results']:
            success, returned_data, status_code, error_msg = api_connection.exec_delete_url('/api/flexiblepower/flexibleassets/' + str(off['pk']) + "/")
            flag=flag and success
            logger.info("Deletion status {success}")
        return flag


    @staticmethod
    def get_asset_flexibility_periodoffers(api_connection, parameters={}):
        """Fetches empty schedule

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/flexiblepower/periodoffers/embedded/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def remove_asset_flexibility_periodoffers(api_connection, extern_asset_id):
        asset_offering=FlexibilityApi.get_asset_flexibility_periodoffers(api_connection, parameters={'flexible_asset__asset__extern_asset_id':extern_asset_id})
        print(asset_offering)
        flag=True
        for off in asset_offering['results']:
            success, returned_data, status_code, error_msg = api_connection.exec_delete_url('/api/flexiblepower/periodoffers/' + str(off['pk']) + "/")
            flag=flag and success
            logger.info("Deletion status {success}")
        return flag

    @staticmethod
    def get_flexible_markets(api_connection,  parameters={}):
        """Fetches empty schedule

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/flexiblepower/flexiblemarkets/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_asset_offer_url(api_connection, asset_offer_pk):
        """Fetches url for a contract type from enum value

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        return api_connection.get_base_url() + '/api/flexiblepower/flexibleassets/' + str(asset_offer_pk) + "/"


    @staticmethod
    def find_flexibility_potential(api_connection, payload):
        logger.info("Lookup flexibility potential")
        success, returned_data, status_code, error_msg = api_connection.exec_post_url(
                '/api/flexiblepower/assetpotential/', payload)
        return success, returned_data, status_code, error_msg

    @staticmethod
    def load_grid_node_polygons(api_connection, grid_nodes:list):
        logger.info("Lookup flexibility potential")
        parameters = {'grid_nodes':grid_nodes}
        print(parameters)
        json_res = api_connection.exec_get_url('/api/flexiblepower/gridnodepolygons/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def upsert_scheduled_regulation(api_connection, scheduled_regulation):
        logger.debug("Upserting scheduled_regulation")
        payload = scheduled_regulation.get_dict(api_connection)
        key = int(payload['pk'])
        logger.info("Saving regulation scheduled key= {} data= {}".format(key, payload))
        if key > 0:
            success, returned_data, status_code, error_msg = api_connection.exec_patch_url(
                '/api/flexiblepower/regulationschedule/' + str(key) + "/", payload)
        else:
            success, returned_data, status_code, error_msg = api_connection.exec_post_url(
                '/api/flexiblepower/regulationschedule/', payload)
        return success, returned_data, status_code, error_msg

    @staticmethod
    def get_regulation_schedule(api_connection, parameters, external_asset_id=None):
        if external_asset_id is not None:
            parameters={
                'flexible_asset__asset__extern_asset_id':external_asset_id
            }
        json_res = api_connection.exec_get_url('/api/flexiblepower/regulationschedule/', parameters)
        if json_res is None:
            return None
        return json_res


    @staticmethod
    def get_external_market_offers(api_connection, parameters):
        """Fetches url for a contract type from enum value

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """

        json_res = api_connection.exec_get_url('/api/flexiblepower/assetsofferedinmarkets/', parameters)
        if json_res is None:
            return None
        return json_res
    @staticmethod
    def get_flexible_market_url(api_connection, flexible_market_pk):
        """Fetches url for a contract type from enum value

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """

        return api_connection.get_base_url() + '/api/flexiblepower/flexiblemarkets/' + str(flexible_market_pk) + "/"

    @staticmethod
    def upsert_market_offering(api_connection, external_market_asset):

        """Creates/Updates master contract agreements

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param master_agreement: master contract agreement object
        :type master_agreement: str, required
        """
        logger.debug("Upserting market offering")
        payload = external_market_asset.get_dict(api_connection)
        key = int(payload['pk'])
        logger.info("Saving external market repr key= {} data= {}".format(key, payload))
        if key > 0:
            success, returned_data, status_code, error_msg = api_connection.exec_patch_url(
                '/api/flexiblepower/assetsofferedinmarkets/' + str(key) + "/", payload)
        else:
            success, returned_data, status_code, error_msg = api_connection.exec_post_url(
                '/api/flexiblepower/assetsofferedinmarkets/', payload)
        return success, returned_data, status_code, error_msg

    @staticmethod
    def remove_market_offering(api_connection, external_asset_id):
        market_offerings=FlexibilityApi.get_external_market_offers(api_connection, {'flexibleasset__asset__extern_asset_id':external_asset_id})
        print(market_offerings)
        for off in market_offerings:
            success, returned_data, status_code, error_msg = api_connection.exec_delete_url('/api/flexiblepower/assetsofferedinmarkets/' + str(off['pk']) + "/")
            print(returned_data)

    @staticmethod
    def get_empty_dispatch_schedule(api_connection):
        """Fetches empty schedule

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param asset_type_enum: type of asset
        :type asset_type_enum: str, required
        """
        json_res = api_connection.exec_get_url('/api/flexiblepower/sampledispatchschedule/')
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_asset_dispatch_schedule(api_connection,  extern_asset_id, period_from, period_until):
        """Fetches asset dispatch schedule

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param extern_asset_id: Asset ID provided by external party (managed in EnergyDesk)
        :type extern_asset_id: str, required
        :param period_from: Start period to load
        :type period_from: str, required
        :param period_until: End period to load
        :type period_until: str, required
        """
        param={'extern_asset_id':extern_asset_id,
               'period_from':period_from,
               'period_until':period_until}
        json_res = api_connection.exec_get_url(
            '/api/flexiblepower/assetdispatchschedule/',param)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_availability_schedule(api_connection, extern_asset_id, period_from, period_until):
        """Fetches empty schedule

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param asset_type_enum: type of asset
        :type asset_type_enum: str, required
        """
        param={'extern_asset_id':extern_asset_id,
               'period_from':period_from,
               'period_until':period_until}
        json_res = api_connection.exec_get_url(
            '/api/flexiblepower/assetavailabilityschedule/',param)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def trade_notification(api_connection,payload):
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/flexiblepower/tradenotification/',
                                                                                 payload)
        if success is False:
            return None
        return json_res

    @staticmethod
    def lookup_asset_registration(api_connection,extern_asset_id):
        return AssetsApi.get_assets_embedded(api_connection, {"extern_asset_id":extern_asset_id})

    @staticmethod
    def lookup_asset_registration_by_mpid(api_connection,mpid):
        return AssetsApi.get_assets_embedded(api_connection, {"meter_id":mpid})

    @staticmethod
    def generate_baselines_for_asset(api_connection, payload):
        success, json_res, status_code, error_msg =BaselinesApi.generate_baselines(api_connection, payload)
        if success is False:
            return None
        return json_res

    @staticmethod
    def register_asset_readings(api_connection, asset_pk, df_readings):
        def convert_series(df):
            df.index=df['datetime']
            df['date'] = pd.to_datetime(df.index)
            df['timestamp'] = df['datetime'].dt.strftime('%Y-%m-%dT%H:%M:%S+01:00')  # Asssuming Norw timezone
            df['date'] = df['date'].dt.strftime('%Y-%m-%d')
            df = df.rename(columns={"consumption": "value"})
            df=df[['timestamp', 'date', 'value']]
            print(df)
            return df.to_json(orient='records')

        payload = {
            'asset': AssetsApi.get_asset_url(api_connection, asset_pk),
            'time_series_type': AssetDataApi.get_timeseries_type_url(api_connection, TimeSeriesTypesEnum.METERREADINGS),
            'quantity_unit': AssetDataApi.get_timeseries_value_unit_url(api_connection, QuantityUnitEnum.KW),
            'quantity_type': AssetDataApi.get_timeseries_value_type_url(api_connection, QuantityTypeEnum.EFFECT),
            'data': convert_series(df_readings),
            'last_updated': str(pendulum.now('Europe/Oslo')),
        }
        print(payload)
        success, json_res, status_code, error_msg = AssetDataApi.upsert_timeseries(api_connection, payload)
        if success is False:
            return None
        return json_res
    @staticmethod
    def register_flexible_asset(api_connection, extern_asset_id,description, meter_id, sub_meter_id,
                                address, city, latitude, longitude, asset_category,asset_type,
                                asset_owner_regnumber,asset_manager_regnumber, dso_regnumber,
                                brp_company_regnumber, callback_url
                                ):
        """Simplified registration of flexible asset

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        payload={
            "extern_asset_id":extern_asset_id,
            "description": description,
            "meter_id": meter_id,
            "sub_meter_id": sub_meter_id,
            "address": address,
            "city": city,
            "latitude":latitude,
            "longitude":longitude,
            "asset_category":asset_category,
            "asset_type":asset_type,
            "asset_owner_regnumber":asset_owner_regnumber,
            "asset_manager_regnumber":asset_manager_regnumber,
            "dso_regnumber":dso_regnumber,
            "brp_company_regnumber":brp_company_regnumber,
            "callback_url":callback_url
        }

        print(json.dumps(payload, indent=2))

        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/flexiblepower/assetregistration/', payload)
        if success is False:
            return None
        return json_res

    @staticmethod
    def register_asset_availability(api_connection, extern_asset_id,
                                    period_from, period_until, crontab, kw_available
                                ):
        """Simplified registration of flexible asset

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        payload={
            "extern_asset_id":extern_asset_id,
            "period_from": period_from,
            "period_until": period_until,
            "crontab": crontab,
            "kw_flexibility": kw_available
        }
        print(json.dumps(payload, indent=2))
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/flexiblepower/specifyassetavailability/', payload)
        if success is False:
            return None
        return json_res
