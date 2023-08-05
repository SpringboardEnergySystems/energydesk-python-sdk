import logging
import pandas as pd
from energydeskapi.geolocation.location_api import LocationApi
from moneyed import EUR
from energydeskapi.sdk.money_utils import FormattedMoney
from energydeskapi.assets.assets_api import AssetsApi
from energydeskapi.customers.customers_api import CustomersApi
from energydeskapi.types.market_enum_types import CommodityTypeEnum, InstrumentTypeEnum,DeliveryTypeEnum,ProfileTypeEnum, BlockSizeEnum, MarketEnum
from energydeskapi.contracts.contracts_api import ContractsApi, Contract
from energydeskapi.types.contract_enum_types import  QuantityTypeEnum,QuantityUnitEnum, ContractTypeEnum, ContractStatusEnum
logger = logging.getLogger(__name__)
#  Change

from energydeskapi.gos.gos_api import GoContract

asset_map={'Nedre Otta'}

def generate_default_gofields( asset_pk, delivery_date, production_from, production_until):
    go=GoContract()
    go.certificates=[]
    go.extra_info=None
    go.asset=None
    go.delivery_date=delivery_date
    go.production_from=production_from
    go.production_until=production_until
    go.asset=asset_pk
    return go

def generate_default_gocontract(api_conn):

    c=Contract()
    c.contract_status=ContractStatusEnum.CONFIRMED
    c.certificates=[]
    c.area="NO1"
    c.quantity_unit=QuantityUnitEnum.LOTS
    c.quantity_type=QuantityTypeEnum.CERTIFICATE
    c.profile_category=ProfileTypeEnum.BASELOAD
    c.quantity=0
    c.delivery_type=DeliveryTypeEnum.FINANCIAL
    c.buy_or_sell="SELL"
    c.instrument_type=InstrumentTypeEnum.FWD
    c.commodity_type=CommodityTypeEnum.GOs
    c.market=MarketEnum.GOs_MARKET
    c.contract_price=FormattedMoney(0, EUR)
    c.contract_type=ContractTypeEnum.GOO
    return c