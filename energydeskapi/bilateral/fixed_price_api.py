import logging
from energydeskapi.sdk.common_utils import check_fix_date2str
from energydeskapi.types.contract_enum_types import QuantityTypeEnum, QuantityUnitEnum
from energydeskapi.sdk.profiles_utils import get_baseload_weekdays, get_baseload_dailyhours, get_baseload_months
logger = logging.getLogger(__name__)

class FixedPriceApi:
    """Class for price calculation

    """
    @staticmethod
    def calculate_contract_price(api_connection ,profile_name, delivery_from, delivery_until, price_area,
                                 monthly_profile=get_baseload_months(), weekday_profile=get_baseload_weekdays(),hours=
                                 get_baseload_dailyhours()):
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
                'profile_name':profile_name,
                "delivery_until": delivery_until,
                "delivery_from": delivery_from,
                "price_area":price_area,
                "monthly_profile":monthly_profile,
                "weekday_profile": weekday_profile,
                "daily_profile": hours
        }

        print(qry_payload)
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/bilateral/contractpricer/external/', qry_payload)
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
    def add_order_from_priceoffer_id(api_connection ,priceoffer_id, buy_or_sell, quantity,
                                     quantity_type=QuantityTypeEnum.VOLUME_YEARLY.name,
                                     quantity_unit=QuantityUnitEnum.KW.name):
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
        logger.info("Adding order")

        qry_payload = {
                "buy_or_sell": buy_or_sell,
                "priceoffer_id": priceoffer_id,
                "quantity":quantity,
                "quantity_type":quantity_type,
                "quantity_unit": quantity_unit
        }

        print(qry_payload)
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/lems/addorderbypriceoffer/', qry_payload)
        return success, json_res, status_code, error_msg