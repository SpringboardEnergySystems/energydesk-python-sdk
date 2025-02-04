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
    def load_meterdata(api_connection,  assets):
        payload={
            'assets':assets
        }
        success, returned_data, status_code, error_msg = api_connection.exec_post_url(
            '/api/flexiblepower/qa/loadmeterdata/', payload)
        return success, returned_data, status_code, error_msg

    @staticmethod
    def load_grouped_meterdata(api_connection,  assets):
        payload={
            'assets':assets
        }
        success, returned_data, status_code, error_msg = api_connection.exec_post_url(
            '/api/flexiblepower/qa/loadgroupedmeterdata/', payload)
        return success, returned_data, status_code, error_msg


