import logging
import pandas as pd
from energydeskapi.geolocation.location_api import LocationApi
from energydeskapi.sdk.money_utils import FormattedMoney, Money, CurrencyCode, gen_json_money, gen_money_from_json
from energydeskapi.sdk.money_utils import FormattedMoney
from energydeskapi.assets.assets_api import AssetsApi
from energydeskapi.customers.customers_api import CustomersApi
from energydeskapi.types.market_enum_types import CommodityTypeEnum, InstrumentTypeEnum,DeliveryTypeEnum,ProfileTypeEnum, BlockSizeEnum, MarketEnum
from energydeskapi.contracts.contracts_api import ContractsApi, Contract
from energydeskapi.types.contract_enum_types import  QuantityTypeEnum,QuantityUnitEnum, ContractTypeEnum, ContractStatusEnum
logger = logging.getLogger(__name__)
#  Change

from energydeskapi.gos.gos_api import GoContract

def generate_product_code_fromgocontract(api_conn, contract):
    if contract.certificates is None or len(contract.certificates)==0:
        return "GoO Contract without Certificate info"
    cert_contract=contract.certificates[0]
    print(cert_contract)
    asset_json=AssetsApi.get_asset_by_key(api_conn, cert_contract.asset)
    print("Asset on GO", asset_json)
    return "GoO_" + asset_json['description'] + "_" + str(cert_contract.delivery_date)[:10]

def generate_product_code(api_conn, contract, gofields):
    asset_json=AssetsApi.get_asset_by_key(api_conn, gofields.asset)
    print(asset_json)
    return "GoO_" + asset_json['description'] + "_" + str(gofields.delivery_date)[:10]

def generate_default_gofields( asset_pk, delivery_date, production_from, production_until):
    go=GoContract()
    go.certificates=[]
    go.extra_info=None
    go.asset=None
    go.support=True
    go.technology="Hydro"
    go.quality=None
    go.flexible_delivery=False
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
    c.contract_price=FormattedMoney(0, CurrencyCode.EUR)
    c.contract_type=ContractTypeEnum.GOO
    c.trading_fee = FormattedMoney(0, CurrencyCode.EUR)
    c.clearing_fee = FormattedMoney(0, CurrencyCode.EUR)
    return c