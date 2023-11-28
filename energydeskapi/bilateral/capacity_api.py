import logging

from energydeskapi.assets.assets_api import AssetsApi
from energydeskapi.customers.customers_api import CustomersApi
from energydeskapi.types.contract_enum_types import QuantityTypeEnum
from energydeskapi.types.contract_enum_types import QuantityUnitEnum
import pendulum
logger = logging.getLogger(__name__)


class AvailabilityTenderInstance():
    def __init__(self,description, period_from, period_until):
        self.pk = 0
        self.description=description
        self.period_from = period_from
        self.period_until = period_until
    def get_dict(self, api_conn):
        dict = {}
        dict['pk'] = self.pk
        if self.description is not None: dict['description'] = self.description
        if self.period_from is not None: dict['period_from'] = self.period_from
        if self.period_until is not None: dict['period_until'] = self.period_until
        return dict

class AvailabilityTender():
  def __init__(self):
    self.pk = 0
    self.description=None
    self.activation_addon=0
    self.grid_component = None
    self.requested_hours = None
    self.tender_open_from = str(pendulum.today("Europe/Oslo"))
    self.tender_open_until = None
    self.availability_period_from = None
    self.availability_period_until = None
    self.instances=[]
  def get_dict(self, api_conn):
    dict = {}
    dict['pk'] = self.pk
    if self.description is not None: dict['description'] = self.description
    #if self.activation_addon is not None: dict['activation_addon'] = self.activation_addon
    if self.grid_component is not None: dict['grid_component'] = AssetsApi.get_asset_url(api_conn, self.grid_component)
    if self.requested_hours is not None: dict['requested_hours'] = self.requested_hours
    if self.tender_open_from is not None: dict['tender_open_from'] = self.tender_open_from
    if self.tender_open_until is not None:
        dict['tender_open_until'] = self.tender_open_until
    elif self.availability_period_until is not None:
        dict['tender_open_until'] = self.availability_period_until
    if self.availability_period_from is not None: dict['availability_period_from'] = self.availability_period_from
    if self.availability_period_until is not None: dict['availability_period_until'] = self.availability_period_until
    lst=[]
    for l in self.instances:
        lst.append(l.get_dict(api_conn))
    dict['instances']=lst
    return dict


class AvailableHours():
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
        json_res = api_connection.exec_get_url('/api/bilateral/availability/tender/calculated/', parameters)
        if json_res is not None:
          return json_res
        return None

    @staticmethod
    def get_capacity_request(api_connection, parameters={}):
        json_res = api_connection.exec_get_url('/api/bilateral/availability/tender/', parameters)
        if json_res is not None:
          return json_res
        return None
    @staticmethod
    def get_capacity_request_by_key(api_connection, pk):
        logger.info("Fetching tenders with key " + str(pk))
        json_res=api_connection.exec_get_url('/api/bilateral/availability/tender/' + str(pk) + "/")
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_capacity_request_embedded(api_connection, parameters={}):
        json_res = api_connection.exec_get_url('/api/bilateral/availability/tender/embedded/', parameters)
        if json_res is not None:
          return json_res
        return None
    @staticmethod
    def get_tender_instance_embedded(api_connection, parameters={}):
        json_res = api_connection.exec_get_url('/api/bilateral/availability/tender/instance/', parameters)
        if json_res is not None:
          return json_res
        return None

    @staticmethod
    def get_capacity_request_url(api_connection, key):
        return api_connection.get_base_url() + '/api/bilateral/availability/tender/' + str(key) + "/"

    @staticmethod
    def list_active_capacity_offers(api_connection, parameters={}):

        logger.info("Retrieve previously given pricees")
        json_res = api_connection.exec_get_url('/api/bilateral/availability/tenderoffers/embedded/', parameters)
        if json_res is not None:
            return json_res
        return []
    @staticmethod
    def get_availability_hours(api_connection, parameters={}):
        json_res = api_connection.exec_get_url('/api/bilateral/availability/availablehours/', parameters)
        if json_res is not None:
          return json_res
        return []

    @staticmethod
    def upsert_capacity_request(api_connection, capacity_profile):
      if capacity_profile.pk > 0:
          success, returned_data, status_code, error_msg = api_connection.exec_patch_url(
              '/api/bilateral/availability/tender/' + str(capacity_profile.pk) + "/", capacity_profile.get_dict(api_connection))
      else:
          success, returned_data, status_code, error_msg = api_connection.exec_post_url(
              '/api/bilateral/availability/tender/', capacity_profile.get_dict(api_connection))
      return success, returned_data, status_code, error_msg
    @staticmethod
    def upsert_availability_hours(api_connection, availability_hours):
      if availability_hours.pk > 0:
          success, returned_data, status_code, error_msg = api_connection.exec_patch_url(
              '/api/bilateral/availability/flexiblehours/' + str(availability_hours.pk) + "/", availability_hours.get_dict(api_connection))
      else:
          success, returned_data, status_code, error_msg = api_connection.exec_post_url(
              '/api/bilateral/availability/flexiblehours/', availability_hours.get_dict(api_connection))
      return success, returned_data, status_code, error_msg
    @staticmethod
    def calculate_capacity_price(api_connection, tender_id, price_addon, activation_price, currency_code="NOK"):
        qry_payload = {
                "currency_code": currency_code,
                "tender_id":tender_id,
                "price_addon": price_addon,
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

        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/lems/addorderbycapacityoffer/', qry_payload)
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
