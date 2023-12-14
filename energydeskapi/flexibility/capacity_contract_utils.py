import logging
import pandas as pd
from energydeskapi.geolocation.location_api import LocationApi
from energydeskapi.sdk.money_utils import FormattedMoney, Money, CurrencyCode, gen_json_money, gen_money_from_json
from energydeskapi.sdk.money_utils import FormattedMoney
from energydeskapi.assets.assets_api import AssetsApi
from energydeskapi.customers.customers_api import CustomersApi
from energydeskapi.types.market_enum_types import CommodityTypeEnum, InstrumentTypeEnum,DeliveryTypeEnum,ProfileTypeEnum, BlockSizeEnum, MarketEnum
from energydeskapi.contracts.contracts_api import ContractsApi, Contract
from energydeskapi.types.contract_enum_types import  QuantityTypeEnum,QuantityUnitEnum, GosTechnologyEnum, ContractTypeEnum, ContractStatusEnum
logger = logging.getLogger(__name__)
#  Change

def generate_default_capacity_contract(api_conn):

    c=Contract()
    c.contract_status=ContractStatusEnum.CONFIRMED

    c.certificates=[]
    c.contract_profile={'periods':[]}
    c.area="NO1"
    c.quantity_unit=QuantityUnitEnum.MW
    c.quantity_type=QuantityTypeEnum.EFFECT
    c.profile_category=ProfileTypeEnum.CONTRACTPROFILE
    c.quantity=0
    c.otc=True
    c.delivery_type=DeliveryTypeEnum.PHYSICAL
    c.buy_or_sell="BUY"
    c.instrument_type=InstrumentTypeEnum.FWD
    c.commodity_type=CommodityTypeEnum.GRID_CAPACITY
    c.market=MarketEnum.NORDIC_POWER
    c.contract_price=FormattedMoney(0, CurrencyCode.NOK)
    c.contract_type=ContractTypeEnum.CAPACITY
    c.trading_fee = FormattedMoney(0, CurrencyCode.NOK)
    c.clearing_fee = FormattedMoney(0, CurrencyCode.NOK)
    return c