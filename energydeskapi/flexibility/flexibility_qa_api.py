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
from energydeskapi.flexibility.datatypes.json_encoder import DateTimeEncoder, date_hook
from typing import List
from dataclasses import dataclass, asdict, field
logger = logging.getLogger(__name__)


class FlexibilityQaApi:
    """ Class for flexibility and prequalification
    """
    @staticmethod
    def get_shortflextransactions_embedded(api_connection,  parameters={}):
        json_res = api_connection.exec_get_url('/api/flexiblepower/qa/flextrades/embedded/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_shortflexassets_embedded(api_connection,  parameters={}):
        json_res = api_connection.exec_get_url('/api/flexiblepower/qa/flextradeassets/embedded/', parameters)
        if json_res is None:
            return None
        return json_res
    @staticmethod
    def get_shortflextransactions(api_connection,  parameters={}):
        json_res = api_connection.exec_get_url('/api/flexiblepower/qa/flextrades/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_longflex_offers_embedded(api_connection,  parameters={}):
        json_res = api_connection.exec_get_url('/api/flexiblepower/qa/longflexroffers/embedded/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_longflex_assets_embedded(api_connection,  parameters={}):
        json_res = api_connection.exec_get_url('/api/flexiblepower/qa/longflexassets/embedded/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_meterdata(api_connection,  parameters={}):
        json_res = api_connection.exec_get_url('/api/flexiblepower/qa/flexassetmeterdata/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def upsert_meterdata(api_connection, key,asset_id, df_meter_data_ams, df_meter_data_submeter):
        payload = {
            'asset_id': asset_id,
            'meter_data_ams': None if df_meter_data_ams is None else json.loads(df_meter_data_ams.to_json(orient='records', date_format='iso')),
            'meter_data_submeter': None if df_meter_data_submeter is None else json.loads(df_meter_data_submeter.to_json(orient='records', date_format='iso')),
        }
        logger.info("Saving regulation scheduled key= {} data= {}".format(key, payload))
        if key > 0:
            success, returned_data, status_code, error_msg = api_connection.exec_patch_url(
                '/api/flexiblepower/qa/flexassetmeterdata/' + str(key) + "/", payload)
        else:
            success, returned_data, status_code, error_msg = api_connection.exec_post_url(
                '/api/flexiblepower/qa/flexassetmeterdata/', payload)
        return success, returned_data, status_code, error_msg

    @staticmethod
    def load_meterdata(api_connection, resolution, assets, longflex_origination=False):
        payload={
            'assets':assets,
            'resolution': resolution,
            'longflex_origination':longflex_origination
        }
        success, returned_data, status_code, error_msg = api_connection.exec_post_url(
            '/api/flexiblepower/qa/loadmeterdata/', payload)
        return success, returned_data, status_code, error_msg

    @staticmethod
    def load_grouped_meterdata(api_connection, resolution,  assets, use_sub_meter=False):
        payload={
            'assets':assets,
            'resolution': resolution,
            'use_sub_meter':use_sub_meter
        }
        print(payload)
        success, returned_data, status_code, error_msg = api_connection.exec_post_url(
            '/api/flexiblepower/qa/loadgroupedmeterdata/', payload)
        return success, returned_data, status_code, error_msg


