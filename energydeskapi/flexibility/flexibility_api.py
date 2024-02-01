import logging
from energydeskapi.types.flexibility_enum_types import ExternalMarketTypeEnums
import pandas as pd
logger = logging.getLogger(__name__)


class ExternalMarketAsset:
    def __init__(self, asset_offered_pk, external_market_asset_id, external_market_name=ExternalMarketTypeEnums.NODES.name, external_market_asset_properties=None):
        self.pk = 0
        self.asset_offered_pk = asset_offered_pk
        self.external_market_name=external_market_name
        self.external_market_asset_id = external_market_asset_id
        self.external_market_asset_properties = external_market_asset_properties

    def get_dict(self, api_conn):
        dict = {}
        dict['pk'] = self.pk
        if self.asset_offered_pk is not None:
            dict['asset_offered'] = FlexibilityApi.get_asset_offer_url(api_conn, self.asset_offered_pk)
        if self.external_market_name is not None:
            dict['external_market'] = self.external_market_name
        if self.external_market_asset_id is not None:
            dict['external_market_asset_id'] = self.external_market_asset_id
        if self.external_market_asset_properties is not None:
            dict['external_market_asset_properties'] = self.external_market_asset_properties
        return dict


class FlexibilityApi:
    """ Class for flexibility
    """

    @staticmethod
    def get_offered_assets(api_connection, parameters={}):
        """Fetches empty schedule

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/flexiblepower/assetsoffered/embedded/', parameters)
        if json_res is None:
            return None
        return json_res


    @staticmethod
    def get_asset_offer_url(api_connection, asset_offer_pk):
        """Fetches url for a contract type from enum value

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """

        return api_connection.get_base_url() + '/api/flexiblepower/assetsoffered/' + str(asset_offer_pk) + "/"

    @staticmethod
    def get_external_market_offers(api_connection, parameters):
        """Fetches url for a contract type from enum value

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """

        json_res = api_connection.exec_get_url('/api/flexiblepower/assetsofferedinmarkets/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def upsert_market_offering(api_connection, external_market_asset):

        """Creates/Updates master contract agreements

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param master_agreement: master contract agreement object
        :type master_agreement: str, required
        """
        logger.debug("Upserting market offering")
        payload = external_market_asset.get_dict(api_connection)
        key = int(payload['pk'])
        if key > 0:
            success, returned_data, status_code, error_msg = api_connection.exec_patch_url(
                '/api/flexiblepower/assetsofferedinmarkets/' + str(key) + "/", payload)
        else:
            success, returned_data, status_code, error_msg = api_connection.exec_post_url(
                '/api/flexiblepower/assetsofferedinmarkets/', payload)
        return success, returned_data, status_code, error_msg

    @staticmethod
    def remove_market_offering(api_connection, external_asset_id):
        market_offerings=FlexibilityApi.get_external_market_offers(api_connection, {'asset_offered__asset__extern_asset_id':external_asset_id})
        print(market_offerings)
        for off in market_offerings:
            success, returned_data, status_code, error_msg = api_connection.exec_delete_url('/api/flexiblepower/assetsofferedinmarkets/' + str(off['pk']) + "/")
            print(returned_data)
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
