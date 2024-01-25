import logging
import pandas as pd
logger = logging.getLogger(__name__)

class FlexibilityApi:
    """ Class for flexibility

    """

    @staticmethod
    def get_offered_assets(api_connection):
        """Fetches empty schedule

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/flexiblepower/assetsoffered/embedded/')
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_empty_dispatch_schedule(api_connection):
        """Fetches empty schedule

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param asset_type_enum: type of asset
        :type asset_type_enum: str, required
        """
        json_res = api_connection.exec_get_url('/api/flexiblepower/generateemptyschedule/')
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_availability_schedule(api_connection, extern_asset_id, period_from, period_until):
        """Fetches empty schedule

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param asset_type_enum: type of asset
        :type asset_type_enum: str, required
        """

        json_res = api_connection.exec_get_url(
            '/api/flexiblepower/assetavailabilityschedule/?extern_asset_id=' + extern_asset_id + "&period_from=" + period_from + "&period_until=" + period_until)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def register_flexible_asset(api_connection, extern_asset_id,description, meter_id, sub_meter_id,
                                address, city, latitude, longitude, asset_category,asset_type,
                                asset_owner_regnumber,asset_manager_regnumber, dso_regnumber,
                                brp_company_regnumber, callback_url
                                ):
        """Simplified registration of flexible asset

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        payload={
            "extern_asset_id":extern_asset_id,
            "description": description,
            "meter_id": meter_id,
            "sub_meter_id": sub_meter_id,
            "address": address,
            "city": city,
            "latitude":latitude,
            "longitude":longitude,
            "asset_category":asset_category,
            "asset_type":asset_type,
            "asset_owner_regnumber":asset_owner_regnumber,
            "asset_manager_regnumber":asset_manager_regnumber,
            "dso_regnumber":dso_regnumber,
            "brp_company_regnumber":brp_company_regnumber,
            "callback_url":callback_url
        }
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/flexiblepower/assetregistration/', payload)
        if success is False:
            return None
        return json_res

    @staticmethod
    def register_asset_availability(api_connection, extern_asset_id,
                                    period_from, period_until, crontab, kw_available
                                ):
        """Simplified registration of flexible asset

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        payload={
            "extern_asset_id":extern_asset_id,
            "period_from": period_from,
            "period_until": period_until,
            "crontab": crontab,
            "kw_flexibility": kw_available
        }
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/flexiblepower/specifyassetavailability/', payload)
        if success is False:
            return None
        return json_res
