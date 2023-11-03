import logging
import pandas as pd
from energydeskapi.geolocation.location_api import LocationApi
from energydeskapi.types.contract_enum_types import GosTechnologyEnum
from energydeskapi.assets.assets_api import AssetsApi
from energydeskapi.customers.customers_api import CustomersApi
from energydeskapi.sdk.common_utils import check_fix_date2str
from energydeskapi.sdk.common_utils import key_from_url
logger = logging.getLogger(__name__)


#  Change
class GoContract:
  """ Class for contracts

  """

  def __init__(self):
    self.pk = 0
    self.extra_info = None
    self.asset = None
    self.production_from = None
    self.support = True
    self.flexible_delivery = False
    self.production_until = None
    self.delivery_date = None
    self.invoice_date = None
    self.invoice_with_mva = None
    self.technology = GosTechnologyEnum.HYDRO.value
    self.quality = []


  def add_quality(self, certificate):
    self.quality.append(certificate)

  def get_dict(self, api_conn):
    dict = {}
    dict['pk'] = self.pk
    if self.production_from is not None: dict['production_from'] = check_fix_date2str(self.production_from)
    if self.production_until is not None: dict['production_until'] = check_fix_date2str(self.production_until)
    if self.asset is not None: dict['asset'] = AssetsApi.get_asset_url(api_conn, self.asset)
    if self.extra_info is not None: dict['extra_info'] = self.extra_info
    if self.invoice_with_mva is not None: dict['invoice_with_mva'] = self.invoice_with_mva
    if self.invoice_date is not None: dict['invoice_date'] = self.invoice_date
    if self.support is not None: dict['support'] = self.support
    if self.flexible_delivery is not None: dict['flexible_delivery'] = self.flexible_delivery
    if self.technology is not None: dict['technology'] = GosApi.get_technology_url(api_conn, self.technology)
    if self.delivery_date is not None: dict['delivery_date'] = check_fix_date2str(self.delivery_date)
    if self.quality is not None and len(self.quality)>0:
      dict['quality'] = self.quality
    print(dict)
    return dict

  @staticmethod
  def from_dict(d):
    c = GoContract()
    c.pk = d['pk']
    c.asset=None if not 'asset' in d else key_from_url(d['asset'])
    c.production_from = None if not 'production_from' in d else d['production_from']
    c.production_until = None if not 'production_until' in d else d['production_until']
    c.support=False if not 'support' in d else key_from_url(d['support'])
    c.flexible_delivery = False if not 'flexible_delivery' in d else d['flexible_delivery']
    c.technology = None if not 'technology' in d else key_from_url(d['technology'])
    c.quality = None if not 'quality' in d else d['quality']
    c.delivery_date = None if not 'delivery_date' in d else d['delivery_date']
    return c


class GosApi:
  """Class for contracts in api
  These are now stored as normal contracts with an added object for the certificate part

  """


  @staticmethod
  def get_quality_url(api_connection, quality_pk):
    """Fetches url for certificates

    :param api_connection: class with API token for use with API
    :type api_connection: str, required
    :param certificate_pk: type of contract
    :type certificate_pk: integer, required
    """
    return api_connection.get_base_url() + '/api/portfoliomanager/go/quality/' + str(quality_pk) + "/"


  @staticmethod
  def get_qualities(api_connection, parameters={}):
    """Fetches certificates from server

    :param api_connection: class with API token for use with API
    :type api_connection: str, required
    :param contract_status_enum: status of contract
    :type contract_status_enum: str, required
    """
    json_res = api_connection.exec_get_url('/api/portfoliomanager/go/quality/', parameters)
    return json_res

  @staticmethod
  def get_qualities_df(api_connection, parameters={}):
    """Fetches all companies in system with basic key+ name infmation

    :param api_connection: class with API token for use with API
    :type api_connection: str, required
    """
    logger.info("Fetching quality list")
    parameters['page_size'] = 1000
    json_res = GosApi.get_qualities(api_connection, parameters)
    if json_res is None:
      return None
    df = pd.DataFrame(data=json_res)
    return df

  @staticmethod
  def get_quality_by_key(api_connection, key):
    """Fetches certificates from server

    :param api_connection: class with API token for use with API
    :type api_connection: str, required
    :param contract_status_enum: status of contract
    :type contract_status_enum: str, required
    """
    json_res = api_connection.exec_get_url('/api/portfoliomanager/go/quality/' + str(key) + "/")
    return json_res


  @staticmethod
  def register_quality(api_connection, shortname, description):
    """Fetches certificates from server

    :param api_connection: class with API token for use with API
    :type api_connection: str, required
    :param contract_status_enum: status of contract
    :type contract_status_enum: str, required
    """
    payload = {
      "code": shortname,
      "description": description
    }
    success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/portfoliomanager/go/quality/',
                                                                             payload)
    return json_res

  @staticmethod
  def get_technology_url(api_connection, tech):
    """Fetches url for certificates

    :param api_connection: class with API token for use with API
    :type api_connection: str, required
    :param certificate_pk: type of contract
    :type certificate_pk: integer, required
    """
    type_pk = tech if isinstance(tech, int) else tech.value
    return api_connection.get_base_url() + '/api/portfoliomanager/go/technology/' + str(type_pk) + "/"



  @staticmethod
  def get_technologies(api_connection, parameters={}):
    json_res = api_connection.exec_get_url('/api/portfoliomanager/go/technology/', parameters)
    if json_res is not None:
      return json_res
    return None