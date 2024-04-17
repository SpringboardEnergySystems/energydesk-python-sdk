import logging
import pandas as pd
from energydeskapi.geolocation.location_api import LocationApi
from energydeskapi.types.contract_enum_types import GosTechnologyEnum, GosSupportEnum
from energydeskapi.assets.assets_api import AssetsApi
from energydeskapi.customers.customers_api import CustomersApi
from energydeskapi.sdk.common_utils import check_fix_date2str
from energydeskapi.sdk.common_utils import key_from_url
logger = logging.getLogger(__name__)


#  Change
class CapacityContract:
  """ Class for contracts
  """
  def __init__(self):
    self.pk = 0
    self.meterpoint_id = None
    self.asset = None
    self.capacity_type=None
  def get_dict(self, api_conn):
    dict = {}
    dict['pk'] = self.pk
    if self.meterpoint_id is not None: dict['meterpoint_id'] = self.meterpoint_id
    if self.capacity_type is not None: dict['capacity_type'] = self.capacity_type
    if self.asset is not None: dict['asset'] = AssetsApi.get_asset_url(api_conn, self.asset)
    return dict
  @staticmethod
  def from_dict(d):
    c = CapacityContract()
    c.pk = d['pk']
    c.asset=None if not 'asset' in d else key_from_url(d['asset'])
    c.meterpoint_id = None if not 'meterpoint_id' in d else d['meterpoint_id']
    c.capacity_type = None if not 'capacity_type' in d else d['capacity_type']
    return c


class CapacityApi:
  """Class for capacity contracts in api
  These are now stored as normal contracts with an added object for the certificate part

  """

  @staticmethod
  def get_capacity_contract_types(api_connection, parameters={}):
    """Fetches certificates from server

    :param api_connection: class with API token for use with API
    :type api_connection: str, required
    :param contract_status_enum: status of contract
    :type contract_status_enum: str, required
    """
    json_res = api_connection.exec_get_url('/api/portfoliomanager/go/quality/', parameters)
    return json_res
