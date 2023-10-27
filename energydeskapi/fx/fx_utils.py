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

from energydeskapi.gos.gos_api import GoContract



def generate_default_fxcontract(api_conn):

    c=Contract()
    c.contract_status=ContractStatusEnum.CONFIRMED
    c.certificates=[]
    c.area="SYS"
    c.quantity_unit=QuantityUnitEnum.LOTS
    c.quantity_type=QuantityTypeEnum.CASH_AMOUNT
    c.profile_category=ProfileTypeEnum.BASELOAD
    c.quantity=0
    c.otc=False
    c.delivery_type=DeliveryTypeEnum.FINANCIAL
    c.buy_or_sell="BUY"
    c.instrument_type=InstrumentTypeEnum.FWD
    c.commodity_type=CommodityTypeEnum.CURRENCY
    c.market=MarketEnum.CURRENCY_MARKET
    c.contract_price=FormattedMoney(0, CurrencyCode.EUR)
    c.contract_type=ContractTypeEnum.FX
    c.trading_fee = FormattedMoney(0, CurrencyCode.EUR)
    c.clearing_fee = FormattedMoney(0, CurrencyCode.EUR)
    return c