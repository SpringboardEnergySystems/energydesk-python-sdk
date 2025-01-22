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



@dataclass(frozen=True)
class FeeRate:
    pk: int
    dd: str # URL
    offered_profile: dict
    offered_capacity_mw: float
    sample_portfolio_meterdata: dict
    @property
    def __dict__(self):
        """
        get a python dictionary
        """
        return asdict(self)
    @property
    def json(self):
        """
        get the json formated string
        """
        return json.dumps(self.__dict__, cls=DateTimeEncoder)





class FeesApi:
    """ Class for flexibility and prequalification
    """


    @staticmethod
    def get_feerates_url(api_connection, value):
        value_pk = value if isinstance(value, int) else value.value
        return api_connection.get_base_url() + '/api/portfoliomanager/feerates/' + str(value_pk) + "/"

    @staticmethod
    def get_feerates(api_connection, parameters={}):
        json_res = api_connection.exec_get_url('/api/portfoliomanager/feerates/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_feerates_embedded(api_connection,  parameters={}):
        json_res = api_connection.exec_get_url('/api/portfoliomanager/feerates/embedded/', parameters)
        if json_res is None:
            return None
        return json_res


    @staticmethod
    def upsert_feerates(api_connection, data: FeeRate):
        logger.debug("Upserting feerates")
        payload = json.loads(data.json)

        if data.pk > 0:
            success, returned_data, status_code, error_msg = api_connection.exec_patch_url(
                '/api/portfoliomanager/feerates/' + str(data.pk) + "/", payload)
        else:
            success, returned_data, status_code, error_msg = api_connection.exec_post_url(
                '/api/portfoliomanager/feerates/', payload)
        return success, returned_data, status_code, error_msg

