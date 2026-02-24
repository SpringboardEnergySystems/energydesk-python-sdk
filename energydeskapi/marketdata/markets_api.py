import json
import logging
from typing import Optional

from energydeskapi.sdk.api_connection import ApiConnection
from energydeskapi.types.market_enum_types import DeliveryTypeEnum, ProfileTypeEnum, InstrumentTypeEnum, \
    CommodityTypeEnum, BlockSizeEnum, MarketEnum, MarketPlaceEnum

logger = logging.getLogger(__name__)


class MarketsApi:
    """Class for markets

    """

    @staticmethod
    def get_market_url(api_connection: ApiConnection, market_enum: int | MarketEnum) -> str:
        """Fetches url for market from enum value

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param market_enum: market
        :type market_enum: str, required
        """
        market = market_enum if isinstance(market_enum, int) else market_enum.value
        return api_connection.get_base_url() +'/api/markets/markets/' + str(market) + "/"

    @staticmethod
    def get_market_place_url(api_connection: ApiConnection, market_place_enum: int | MarketPlaceEnum) -> str:
        """Fetches url for market from enum value

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param market_enum: market
        :type market_enum: str, required
        """
        market_place = market_place_enum if isinstance(market_place_enum, int) else market_place_enum.value
        return f"{api_connection.get_base_url()}/api/markets/marketplaces/{market_place}/"

    @staticmethod
    def get_market_obj(api_connection: ApiConnection, market_enum: MarketEnum):
        """Fetches all markets objects with URL relations. Will only return markets for which the user has rights

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """

        json_res=api_connection.exec_get_url('/api/markets/markets/' + str(market_enum.value) + "/")
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_markets(api_connection: ApiConnection, parameters: dict={}) -> Optional[list[dict]]:
        """Fetches all markets objects with URL relations. Will only return markets for which the user has rights

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """

        json_res=api_connection.exec_get_url('/api/markets/markets/', parameters)
        return json_res

    @staticmethod
    def get_market_places(api_connection: ApiConnection, parameters: dict={}) -> Optional[list[dict]]:
        """Fetches all markets objects with URL relations. Will only return markets for which the user has rights

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """

        json_res=api_connection.exec_get_url('/api/markets/marketplaces/', parameters)
        return json_res

    @staticmethod
    def get_markets_df(api_connection: ApiConnection, parameters: dict={}) -> Optional[list[dict]]:
        """Fetches all markets objects with URL relations. Will only return markets for which the user has rights

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """

        json_res=MarketsApi.get_markets(api_connection, parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_instrument_type_url(api_connection: ApiConnection, instrument_type_enum: int | InstrumentTypeEnum) -> str:
        """Fetches url for instrument type from enum value

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param instrument_type_enum: type of instrument
        :type instrument_type_enum: str, required
        """
        instrument_type = instrument_type_enum if isinstance(instrument_type_enum, int) else instrument_type_enum.value
        return api_connection.get_base_url() +'/api/markets/instrumenttypes/' + str(instrument_type) + "/"

    @staticmethod
    def get_instrument_type_obj(api_connection: ApiConnection, instrument_type_enum: InstrumentTypeEnum) -> Optional[dict]:
        """Fetches all instrument type objects with URL relations. Will only return instrument types for which the user has rights

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param instrument_type_enum: type of instrument
        :type instrument_type_enum: str, required
        """

        json_res=api_connection.exec_get_url('/api/markets/instrumenttypes/' + str(instrument_type_enum.value) + "/")
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_delivery_type_url(api_connection: ApiConnection, delivery_type_enum: int | DeliveryTypeEnum) -> str:
        """Fetches url for commodity type from enum value

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param delivery_type_enum: type of commodity
        :type delivery_type_enum: str, required
        """
        deltype = delivery_type_enum if isinstance(delivery_type_enum, int) else delivery_type_enum.value
        return api_connection.get_base_url() +'/api/markets/deliverytypes/' + str(deltype) + "/"

    @staticmethod
    def get_profile_type_url(api_connection: ApiConnection, profile_type_enum: int | ProfileTypeEnum) -> str:
        """Fetches url for commodity type from enum value

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param delivery_type_enum: type of commodity
        :type delivery_type_enum: str, required
        """
        deltype = profile_type_enum if isinstance(profile_type_enum, int) else profile_type_enum.value
        return api_connection.get_base_url() +'/api/markets/profiletypes/' + str(deltype) + "/"

    @staticmethod
    def get_delivery_type_obj(api_connection: ApiConnection, delivery_type_enum: DeliveryTypeEnum) -> Optional[dict]:
        """Fetches all commodity type objects with URL relations. Will only return commodity types for which the user has rights

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param commodity_type_enum: type of commodity
        :type commodity_type_enum: str, required
        """

        json_res=api_connection.exec_get_url('/api/markets/deliverytypes/' + str(delivery_type_enum.value) + "/")
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_commodity_type_url(api_connection: ApiConnection, commodity_type_enum: int | CommodityTypeEnum) -> str:
        """Fetches url for commodity type from enum value

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param commodity_type_enum: type of commodity
        :type commodity_type_enum: str, required
        """
        comm_type = commodity_type_enum if isinstance(commodity_type_enum, int) else commodity_type_enum.value
        return api_connection.get_base_url() +'/api/markets/commoditytypes/' + str(comm_type) + "/"

    @staticmethod
    def get_commodity_type_obj(api_connection: ApiConnection, commodity_type_enum: CommodityTypeEnum) -> Optional[dict]:
        """Fetches all commodity type objects with URL relations. Will only return commodity types for which the user has rights

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param commodity_type_enum: type of commodity
        :type commodity_type_enum: str, required
        """

        json_res=api_connection.exec_get_url('/api/markets/commoditytypes/' + str(commodity_type_enum.value) + "/")
        if json_res is None:
            return None
        return json_res


    @staticmethod
    def get_commodity_types(api_connection: ApiConnection, parameters: dict={}) -> Optional[list[dict]]:
        """Fetches all commodity types

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """

        json_res=api_connection.exec_get_url('/api/markets/commoditytypes/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_commodity(api_connection: ApiConnection, parameters: dict={}) -> Optional[dict]:
        """Fetches all commodity types

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """

        json_res=api_connection.exec_get_url('/api/markets/commoditydefinitions/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_instrument_types(api_connection: ApiConnection, parameters: dict={}) -> Optional[list[dict]]:
        """Fetches all commodity types

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """

        json_res=api_connection.exec_get_url('/api/markets/instrumenttypes/', parameters)
        if json_res is None:
            return None
        return json_res


    @staticmethod
    def get_blocksize_category_url(api_connection: ApiConnection, blocksize_category_enum: BlockSizeEnum) -> str:
        """Fetches blocksize category from url

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param blocksize_category_enum: category of blocksize
        :type blocksize_category_enum: str, required
        """
        return api_connection.get_base_url() +'/api/markets/blocksizecategories/' + str(blocksize_category_enum.value) + "/"

    @staticmethod
    def get_blocksize_category_obj(api_connection: ApiConnection, blocksize_category_enum: BlockSizeEnum) -> Optional[dict]:
        """Fetches all blocksize category objects with URL relations. Will only return blocksize categories for which the user has rights

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param blocksize_category_enum: category of blocksize
        :type blocksize_category_enum: str, required
        """

        json_res=api_connection.exec_get_url('/api/markets/blocksizecategories/' + str(blocksize_category_enum.value) + "/")
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def send_market_update(api_connection: ApiConnection, record_type="prices", marketdata={}):
      payload={
        "record_type":record_type,
        "datarecord":json.loads(json.dumps(marketdata))
      }
      success, returned_data, status_code, error_msg  = api_connection.exec_post_url("/api/markets/updated-marketdata/",
                                                                                     payload=payload)
      return returned_data