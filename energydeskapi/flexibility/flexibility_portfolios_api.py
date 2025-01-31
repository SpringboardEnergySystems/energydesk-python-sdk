import logging
import json
from energydeskapi.assets.assets_api import AssetsApi
from energydeskapi.types.asset_enum_types import TimeSeriesTypesEnum
from energydeskapi.types.baselines_enum_types import BaselinesModelsEnums
from energydeskapi.types.contract_enum_types import QuantityTypeEnum, QuantityUnitEnum
from energydeskapi.assetdata.assetdata_api import AssetDataApi
import pendulum
from energydeskapi.assetdata.baselines_api import BaselinesApi
from energydeskapi.types.flexibility_enum_types import ExternalMarketTypeEnums
import pandas as pd
from datetime import timezone, datetime, date
import json, pendulum
from energydeskapi.contracts.contracts_api import ContractsApi
from energydeskapi.types.contract_enum_types import QuantityTypeEnum, QuantityUnitEnum
from energydeskapi.types.flexibility_enum_types import RegulationTypeEnums
from json import JSONEncoder
from dataclasses import dataclass
from energydeskapi.flexibility.datatypes.json_encoder import DateTimeEncoder, date_hook
from typing import List
from dataclasses import dataclass, asdict, field
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FlexAsset:
    asset_guid_id: str
    @property
    def json(self):
        """
        get the json formated string
        """
        return self.asset_guid_id#json.dumps(self.__dict__, cls=DateTimeEncoder)

@dataclass(frozen=True)
class FlexPortfolio:
    pk: int
    description: str
    portfolio_id: str
    external_id: str
    location: str
    portfolio_asset_list: List[FlexAsset] = field(default_factory=list)
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




@dataclass(frozen=True)
class FlexPortfolioStatus:
    pk: int
    portfolio: str # URL
    status_type: str # URL
    timestamp_from: datetime
    timestamp_until: datetime
    tiggered_by_trade: str # URL
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




@dataclass(frozen=True)
class FlexPortfolioOrder:
    pk: int
    external_order_id: str
    portfolio: str # URL
    regulating_direction: str # URL
    reserves_category: str  # URL
    area_location_id: str # URL
    area_location_name: str  # URL
    isp_period_from: datetime
    isp_period_until: datetime
    order_time: datetime
    buy_or_sell: str
    price_amount: float
    price_currency: str
    quantity: float
    quantity_type: str # URL
    quantity_unit: str# URL
    order_status: str# URL
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




@dataclass(frozen=True)
class FlexPortfolioTrade:
    pk: int
    contract: str # URL
    flexible_portfolio: str # URL
    regulating_direction: str # URL
    reserves_category: str  # URL
    order_data: dict

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



class FlexibilityPortfolioApi:
    """ Class for flexibility and portfolios
    """


    @staticmethod
    def get_flexorder_status_url(api_connection, order_status):
        status_pk = order_status if isinstance(order_status, int) else order_status.value
        return api_connection.get_base_url() + '/api/flexiblepower/flexorderstatuses/' + str(status_pk) + "/"

    @staticmethod
    def get_flexible_portfolio_url(api_connection, pk):
        """Fetches url for a contract type from enum value
        """
        return api_connection.get_base_url() + '/api/flexiblepower/flexibleportfolios/' + str(pk) + "/"

    @staticmethod
    def get_flexible_portfolio_status_type_url(api_connection, portfolio_status):
        """Fetches url for a contract type from enum value
        """
        status_pk = portfolio_status if isinstance(portfolio_status, int) else portfolio_status.value
        return api_connection.get_base_url() + '/api/flexiblepower/portfoliostatustypes/' + str(status_pk) + "/"

    @staticmethod
    def get_flexible_portfolios(api_connection,  parameters={}):
        json_res = api_connection.exec_get_url('/api/flexiblepower/flexibleportfolios/', parameters)
        if json_res is None:
            return None
        return json_res



    @staticmethod
    def get_flexible_portfolios_embedded(api_connection,  parameters={}):
        json_res = api_connection.exec_get_url('/api/flexiblepower/flexibleportfolios/embedded/', parameters)
        if json_res is None:
            return None
        return json_res


    @staticmethod
    def get_portfolio_availability(api_connection, flex_portfolio_id, period_from, period_until):
        param={'portfolio_id':flex_portfolio_id,
               'period_from':period_from,
               'period_until':period_until}
        json_res = api_connection.exec_get_url(
            '/api/flexiblepower/flexportfolioavailability/',param)
        if json_res is None:
            return None
        return json_res


    @staticmethod
    def upsert_flexible_portfolio(api_connection, flex_portfolio: FlexPortfolio):
        logger.debug("Upserting flex portfolio")
        payload = json.loads(flex_portfolio.json)
        key = int(flex_portfolio.pk)
        logger.debug("Saving regulation scheduled key= {} data= {}".format(key, payload))
        if key > 0:
            success, returned_data, status_code, error_msg = api_connection.exec_patch_url(
                '/api/flexiblepower/flexibleportfolios/' + str(key) + "/", payload)
        else:
            success, returned_data, status_code, error_msg = api_connection.exec_post_url(
                '/api/flexiblepower/flexibleportfolios/', payload)
        return success, returned_data, status_code, error_msg


    @staticmethod
    def get_flexible_portfolios_status(api_connection,  parameters={}):
        json_res = api_connection.exec_get_url('/api/flexiblepower/flexibleportfoliostatuses/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def upsert_flexible_portfolio_status(api_connection, flex_portfolio_status: FlexPortfolioStatus):
        logger.debug("Upserting flex portfolio status")
        payload = json.loads(flex_portfolio_status.json)
        key = int(flex_portfolio_status.pk)
        logger.debug("Saving regulation scheduled key= {} data= {}".format(key, payload))
        if key > 0:
            success, returned_data, status_code, error_msg = api_connection.exec_patch_url(
                '/api/flexiblepower/flexibleportfoliostatuses/' + str(key) + "/", payload)
        else:
            success, returned_data, status_code, error_msg = api_connection.exec_post_url(
                '/api/flexiblepower/flexibleportfoliostatuses/', payload)
        return success, returned_data, status_code, error_msg

    @staticmethod
    def get_flexible_portfolios_trades(api_connection,  parameters={}):
        json_res = api_connection.exec_get_url('/api/flexiblepower/flexibleportfoliotrades/', parameters)
        if json_res is None:
            return None
        return json_res
    @staticmethod
    def get_flexible_portfolios_trades_embedded(api_connection,  parameters={}):
        json_res = api_connection.exec_get_url('/api/flexiblepower/flexibleportfoliotrades/embedded/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def upsert_flexible_portfolio_trade(api_connection, flex_portfolio_trade: FlexPortfolioTrade):
        logger.debug("Upserting flex portfolio status")
        payload = json.loads(flex_portfolio_trade.json)
        key = int(flex_portfolio_trade.pk)
        logger.debug("Saving flex order key= {} data= {}".format(key, payload))
        if key > 0:
            success, returned_data, status_code, error_msg = api_connection.exec_patch_url(
                '/api/flexiblepower/flexibleportfoliotrades/' + str(key) + "/", payload)
        else:
            success, returned_data, status_code, error_msg = api_connection.exec_post_url(
                '/api/flexiblepower/flexibleportfoliotrades/', payload)
        return success, returned_data, status_code, error_msg

    @staticmethod
    def get_flexible_portfolios_orders(api_connection,  parameters={}):
        json_res = api_connection.exec_get_url('/api/flexiblepower/flexibleportfolioorders/', parameters)
        if json_res is None:
            return None
        return json_res
    @staticmethod
    def get_flexible_portfolios_orders_embedded(api_connection,  parameters={}):
        json_res = api_connection.exec_get_url('/api/flexiblepower/flexibleportfolioorders/embedded/', parameters)
        if json_res is None:
            return None
        return json_res
    @staticmethod
    def upsert_flexible_portfolio_order(api_connection, flex_portfolio_order: FlexPortfolioOrder):
        logger.debug("Upserting flex portfolio status")
        payload = json.loads(flex_portfolio_order.json)
        key = int(flex_portfolio_order.pk)
        logger.debug("Saving flex order key= {} data= {}".format(key, payload))
        if key > 0:
            success, returned_data, status_code, error_msg = api_connection.exec_patch_url(
                '/api/flexiblepower/flexibleportfolioorders/' + str(key) + "/", payload)
        else:
            success, returned_data, status_code, error_msg = api_connection.exec_post_url(
                '/api/flexiblepower/flexibleportfolioorders/', payload)
        return success, returned_data, status_code, error_msg