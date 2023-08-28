import json
import logging
from typing import List
from datetime import date, datetime
from dataclasses import dataclass, asdict, field
from datetime import timezone, datetime, date
import json
from json import JSONEncoder
from dataclasses import dataclass
from energydeskapi.assets.assets_api import AssetsApi, AssetSubType, Asset, AssetTechData
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.assetdata.baselines_api import BaselinesApi
from energydeskapi.types.asset_enum_types import AssetCategoryEnum
from energydeskapi.types.baselines_enum_types import BaselinesModelsEnums
from energydeskapi.assetdata.baselines_api import BaselinesApi
from energydeskapi.types.common_enum_types import PeriodResolutionEnum
logger = logging.getLogger(__name__)


class PeriodResolutionEncoder(JSONEncoder):
    # Override the default method
    def default(self, obj):
        if isinstance(obj, (PeriodResolutionEnum)):
            return obj.value
@dataclass
class BaselineStdAlgoParams:
    resolution: PeriodResolutionEnum
    periods_predicted: int
    periods_shifted: int
    extra_parameter1: str=None
    extra_parameter2: str = None
    @property
    def json(self):
        """
        get the json formated string
        """
        return json.dumps(self.__dict__, cls=PeriodResolutionEncoder)
def create_default_algo_parameters(algorithm):
    if algorithm==BaselinesModelsEnums.BUSINESSDAY_PROFILE:
        return BaselineStdAlgoParams(PeriodResolutionEnum.HOURLY, periods_predicted=24, periods_shifted=0)

    return BaselineStdAlgoParams(PeriodResolutionEnum.HOURLY, periods_predicted=24, periods_shifted=0)


def initialize_standard_algorithms(api_conn):
    algoinstance={
        'description':'Standard Weekday',
        'algorithm': BaselinesApi.get_baselines_algorithm_url(api_conn, BaselinesModelsEnums.BUSINESSDAY_PROFILE),
        'algorithm_parameters':create_default_algo_parameters(BaselinesModelsEnums.BUSINESSDAY_PROFILE).json,
        'resolution': BaselinesApi.get_baselines_resolutions_url(api_conn,PeriodResolutionEnum.HOURLY),
        'enabled': True,
    }
    success, returned_data, status_code, error_msg=BaselinesApi.upsert_algorithm_instance(api_conn, algoinstance)


