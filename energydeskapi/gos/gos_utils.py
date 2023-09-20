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

def generate_product_code(api_conn, contract, gofields):
    asset_json=AssetsApi.get_asset_by_key(api_conn, gofields.asset)
    print(asset_json)
    return "GoO_" + asset_json['description'] + "_" + str(gofields.delivery_date)
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
    c.quantity_unit=QuantityUnitEnum.MW
    c.quantity_type=QuantityTypeEnum.VOLUME
    c.profile_category=ProfileTypeEnum.BASELOAD
    c.quantity=0
    c.otc=True
    c.delivery_type=DeliveryTypeEnum.PHYSICAL
    c.buy_or_sell="SELL"
    c.instrument_type=InstrumentTypeEnum.FWD
    c.commodity_type=CommodityTypeEnum.GOs
    c.market=MarketEnum.GOs_MARKET
    c.contract_price=FormattedMoney(0, EUR)
    c.contract_type=ContractTypeEnum.GOO
    c.trading_fee = FormattedMoney(0, EUR)
    c.clearing_fee = FormattedMoney(0, EUR)
    return c