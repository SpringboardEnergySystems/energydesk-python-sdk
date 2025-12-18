import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime

from energydeskapi.flexibility.datatypes.json_encoder import DateTimeEncoder
from energydeskapi.sdk.api_connection import ApiConnection
from energydeskapi.types.contract_enum_types import FeeTypeEnum

logger = logging.getLogger(__name__)



@dataclass(frozen=True)
class FeeRate:
    pk: int
    fee_type: str # URL
    commodity_type: str # URL
    instrument_type: str  # URL
    market: str  # URL
    participant: str  # URL
    valid_from: datetime
    valid_until: datetime
    fee_rate: float
    fee_rate_currency: str
    block_size_category: str
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
    def get_feetype_url(api_connection: ApiConnection, value:FeeTypeEnum):
        value_pk = value if isinstance(value, int) else value.value
        return api_connection.get_base_url() + '/api/portfoliomanager/feetypes/' + str(value_pk) + "/"

    @staticmethod
    def get_feetypes(api_connection: ApiConnection,  parameters={}):
        json_res = api_connection.exec_get_url('/api/portfoliomanager/feetypes/', parameters)
        if json_res is None:
            return None
        return json_res


    @staticmethod
    def get_feerates_url(api_connection: ApiConnection, value):
        value_pk = value if isinstance(value, int) else value.value
        return api_connection.get_base_url() + '/api/portfoliomanager/feerates/' + str(value_pk) + "/"

    @staticmethod
    def get_feerates(api_connection: ApiConnection, parameters: dict={}):
        json_res = api_connection.exec_get_url('/api/portfoliomanager/feerates/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_feerates_embedded(api_connection: ApiConnection,  parameters={}):
        json_res = api_connection.exec_get_url('/api/portfoliomanager/feerates/embedded/', parameters)
        if json_res is None:
            return None
        return json_res


    @staticmethod
    def upsert_feerates(api_connection: ApiConnection, data: FeeRate):
        logger.debug("Upserting feerates")
        payload = json.loads(data.json)

        if data.pk > 0:
            success, returned_data, status_code, error_msg = api_connection.exec_patch_url(
                '/api/portfoliomanager/feerates/' + str(data.pk) + "/", payload)
        else:
            success, returned_data, status_code, error_msg = api_connection.exec_post_url(
                '/api/portfoliomanager/feerates/', payload)
        return success, returned_data, status_code, error_msg

