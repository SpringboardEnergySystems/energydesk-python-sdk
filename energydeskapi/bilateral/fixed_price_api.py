import logging
from energydeskapi.sdk.common_utils import check_fix_date2str
from energydeskapi.types.common_enum_types import PeriodResolutionEnum
from energydeskapi.types.contract_enum_types import QuantityTypeEnum, QuantityUnitEnum
from energydeskapi.sdk.profiles_utils import get_baseload_weekdays, get_baseload_dailyhours, get_baseload_months
logger = logging.getLogger(__name__)

class FixedPriceApi:
    """Class for price calculation

    """
    @staticmethod
    def calculate_contract_price(api_connection , delivery_from, delivery_until, price_area,
                                 profile_type="BASELOAD", custom_profile_key=None):
        """Calculated fix price in period

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param delivery_from: period from
        :type from_period: str, required
        :param delivery_until: period to
        :type until_period: str, required
        :param price_area: price area
        :type price_area: str, required
        """
        logger.info("Calculate bilateral fix price")

        qry_payload = {
                "delivery_until": delivery_until,
                "delivery_from": delivery_from,
                "price_area":price_area,
                'profile_type': profile_type
        }
        if custom_profile_key is not None:
            qry_payload['custom_profile_key']= custom_profile_key


        print(qry_payload)
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/bilateral/contractpricer/external/', qry_payload)
        return success, json_res, status_code, error_msg


    @staticmethod
    def query_deliveries(api_connection ,period_from, period_until, resolution=PeriodResolutionEnum.DAILY.value, area_filter=None):
        qry_payload = {
                "period_from": period_from,
                "period_until": period_until,
                "resolution":resolution,
        }
        if area_filter is not None:
            qry_payload['area_filter']=area_filter
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/bilateral/deliveries/external/', qry_payload)
        return success, json_res, status_code, error_msg

    @staticmethod
    def list_active_price_offers(api_connection, parameters={}):
        """Calculated fix price in period

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Retrieve previously given pricees")

        json_res = api_connection.exec_get_url('/api/bilateral/priceoffers/', parameters)
        if json_res is not None:
            return json_res
        return None

    @staticmethod
    def get_avaiable_fixprice_periods(api_connection):
        """Fetches pricing configurations

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching current open fixprice periods")
        json_res = api_connection.exec_get_url(
            '/api/bilateral/contractpricer/allowedperiods/')
        return json_res

    @staticmethod
    def add_order_from_priceoffer_id(api_connection ,priceoffer_id, buy_or_sell, quantity,
                                     quantity_type=QuantityTypeEnum.VOLUME_YEARLY.name,
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
                "quantity_type":quantity_type,
                "quantity_unit": quantity_unit
        }

        logger.info(str(qry_payload))
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/lems/addorderbypriceoffer/', qry_payload)
        return success, json_res, status_code, error_msg
