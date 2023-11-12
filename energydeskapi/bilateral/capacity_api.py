import logging

from energydeskapi.assets.assets_api import AssetsApi
from energydeskapi.customers.customers_api import CustomersApi
from energydeskapi.types.contract_enum_types import QuantityTypeEnum
from energydeskapi.types.contract_enum_types import QuantityUnitEnum

logger = logging.getLogger(__name__)
class CapacityRequest():
  def __init__(self):
    self.pk = 0
    self.description=None
    self.grid_component = None
    self.requested_profile = None
    self.period_from = None
    self.period_until = None

  def get_dict(self, api_conn):
    dict = {}
    dict['pk'] = self.pk
    if self.description is not None: dict['description'] = self.description
    if self.grid_component is not None: dict['grid_component'] = AssetsApi.get_asset_url(api_conn, self.grid_component)
    if self.requested_profile is not None: dict['requested_profile'] = self.requested_profile
    if self.period_from is not None: dict['period_from'] = self.period_from
    if self.period_until is not None: dict['period_until'] = self.period_until
    return dict


class AvaulabilityProfile():
  def __init__(self):
    self.pk = 0
    self.company_pk = 0
    self.request_response_pk=0
    self.availability = None
    self.period_from = None
    self.period_until = None

  def get_dict(self, api_conn):
    dict = {}
    dict['pk'] = self.pk
    if self.company_pk is not None: dict['company'] = CustomersApi.get_company_url(api_conn, self.company_pk)
    if self.request_response_pk is not None: dict['request_response'] = CapacityApi.get_capacity_request_url(api_conn, self.request_response_pk)
    if self.availability is not None: dict['availability'] = self.availability
    if self.period_from is not None: dict['period_from'] = self.period_from
    if self.period_until is not None: dict['period_until'] = self.period_until

    return dict

class RatesConfiguration:
    def __init__(self):
        self.pk = 0
        self.standby_addon_kwh=2
        self.volatility_rate = 0.4
        self.riskfree_rate = 0.03



    def get_dict(self,api_conn):
        dict = {}
        dict['pk']=self.pk
        dict['standby_addon_kwh'] = self.standby_addon_kwh
        dict['volatility_rate'] = self.volatility_rate
        dict['riskfree_rate'] = self.riskfree_rate
        return dict


class CapacityApi:

    @staticmethod
    def get_capacity_profile(api_connection, parameters={}):
        json_res = api_connection.exec_get_url('/api/bilateral/capacity/request/calculated/', parameters)
        if json_res is not None:
          return json_res
        return None

    @staticmethod
    def get_capacity_request(api_connection, parameters={}):
        json_res = api_connection.exec_get_url('/api/bilateral/capacity/request/', parameters)
        if json_res is not None:
          return json_res
        return None
    @staticmethod
    def get_capacity_request_by_key(api_connection, pk):
        logger.info("Fetching tenders with key " + str(pk))
        json_res=api_connection.exec_get_url('/api/bilateral/capacity/request/' + str(pk) + "/")
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_capacity_request_embedded(api_connection, parameters={}):
        json_res = api_connection.exec_get_url('/api/bilateral/capacity/request/embedded/', parameters)
        if json_res is not None:
          return json_res
        return None
    @staticmethod
    def get_capacity_request_url(api_connection, key):
        return api_connection.get_base_url() + '/api/bilateral/capacity/request/' + str(key) + "/"

    @staticmethod
    def list_active_capacity_offers(api_connection, parameters={}):

        logger.info("Retrieve previously given pricees")
        json_res = api_connection.exec_get_url('/api/bilateral/capacity/offers/embedded/', parameters)
        if json_res is not None:
            return json_res
        return None
    @staticmethod
    def get_availability_hours(api_connection, parameters={}):
        json_res = api_connection.exec_get_url('/api/bilateral/capacity/availablehours/', parameters)
        if json_res is not None:
          return json_res
        return None

    @staticmethod
    def upsert_capacity_request(api_connection, capacity_profile):
      if capacity_profile.pk > 0:
          success, returned_data, status_code, error_msg = api_connection.exec_patch_url(
              '/api/bilateral/capacity/request/' + str(capacity_profile.pk) + "/", capacity_profile.get_dict(api_connection))
      else:
          success, returned_data, status_code, error_msg = api_connection.exec_post_url(
              '/api/bilateral/capacity/request/', capacity_profile.get_dict(api_connection))
      return success, returned_data, status_code, error_msg
    @staticmethod
    def upsert_availability_hours(api_connection, availability_hours):
      if availability_hours.pk > 0:
          success, returned_data, status_code, error_msg = api_connection.exec_patch_url(
              '/api/bilateral/capacity/availablehours/' + str(availability_hours.pk) + "/", availability_hours.get_dict(api_connection))
      else:
          success, returned_data, status_code, error_msg = api_connection.exec_post_url(
              '/api/bilateral/capacity/availablehours/', availability_hours.get_dict(api_connection))
      return success, returned_data, status_code, error_msg
    @staticmethod
    def calculate_capacity_price(api_connection, periods, substation_profile, current_price, activation_price, currency_code="NOK"):
        dict_periods=[]
        for p in periods:
            dict_periods.append({
            "period_tag": p[0],
            "contract_date_from":p[1],
            "contract_date_until": p[2],
            })
        qry_payload = {
                "currency_code": currency_code,
                "substation_profile":substation_profile,
                "periods":dict_periods,
                "current_price": current_price,
                "activation_price":activation_price
        }
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/bilateral/contractpricer/capacity/', qry_payload)
        return success, json_res, status_code, error_msg

    @staticmethod
    def calculate_capacity_price_externals(api_connection,tender_id, availability_hours, max_hours_activation, activation_price, currency_code="NOK"):

        payload = {
                "tender_id":tender_id,
                "currency_code": currency_code,
                "max_hours":max_hours_activation,
                "availability_hours": availability_hours,
                "activation_price":activation_price
        }
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/bilateral/contractpricer/capacity/externals/', payload)
        return success, json_res, status_code, error_msg
    @staticmethod
    def add_order_from_priceoffer_id(api_connection ,priceoffer_id, buy_or_sell, quantity,
                                     quantity_type=QuantityTypeEnum.VOLUME_YEARLY.name,
                                     quantity_unit=QuantityUnitEnum.KW.name):
        """Add order with reference to a price quote
        """
        logger.info("Adding order")

        qry_payload = {
                "buy_or_sell": buy_or_sell,
                "priceoffer_id": priceoffer_id,
                "quantity":quantity,
                "quantity_type":quantity_type,
                "quantity_unit": quantity_unit
        }

        logger.info(str(qry_payload))
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/lems/addorderbypriceoffer/', qry_payload)
        return success, json_res, status_code, error_msg


    @staticmethod
    def add_order_from_capacityoffer_id(api_connection ,priceoffer_id, buy_or_sell, quantity,quantity_type=QuantityTypeEnum.EFFECT.name,
                                     quantity_unit=QuantityUnitEnum.KW.name):
        """Add order with reference to a price quote

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param buy_or_sell: period from
        :type buy_or_sell: str, required
        :param priceoffer_id: GUID repr price offer
        :type priceoffer_id: str, GUID as str
        :param quantity: quantity
        :type quantity: float, quantity requested
        """
        logger.info("Adding order")

        qry_payload = {
                "buy_or_sell": buy_or_sell,
                "priceoffer_id": priceoffer_id,
                "quantity":quantity,
            "quantity_type": quantity_type,
            "quantity_unit": quantity_unit
        }

        logger.info(str(qry_payload))
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/lems/addorderbycapacityoffer/', qry_payload)
        return success, json_res, status_code, error_msg

    @staticmethod
    def get_rates_configurations(api_connection):
        """Fetches pricing configurations

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching capacity rates configurations")
        json_res = api_connection.exec_get_url(
            '/api/bilateral/capacity/ratesconfigurations/')
        return json_res

    @staticmethod
    def upsert_rates_configuration(api_connection, pricing_conf):
        logger.info("Registering capacity rates configuration")
        if type(pricing_conf) is dict:
            pk = pricing_conf['pk']
            pricing_dict = pricing_conf
        else:
            pk = pricing_conf.pk
            pricing_dict = pricing_conf.get_dict(api_connection)
        print(pricing_dict)
        if pk > 0:
            success, returned_data, status_code, error_msg = api_connection.exec_patch_url(
                '/api/bilateral/capacity/ratesconfigurations/' + str(pk) + "/", pricing_dict)
        else:
            success, returned_data, status_code, error_msg = api_connection.exec_post_url(
                '/api/bilateral/capacity/ratesconfigurations/', pricing_dict)
        return success, returned_data, status_code, error_msg


    @staticmethod
    def get_rates_configuration_by_pk(api_connection, pk):
        """Fetches pricing configuration from pk

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching capacity configuration")
        json_res = api_connection.exec_get_url(
            '/api/bilateral/capacity/ratesconfigurations/' + str(pk) + '/')
        return json_res
