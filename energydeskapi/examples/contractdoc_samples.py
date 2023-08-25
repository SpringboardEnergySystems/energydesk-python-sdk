import logging
from energydeskapi.contracts.contracts_api import ContractsApi, Contract, ContractFilter, ContractTag
from energydeskapi.contracts.dealcapture import bilateral_dealcapture
from energydeskapi.contracts.masteragreement_api import MasterAgreementApi, MasterContractAgreement
from energydeskapi.gos.gos_api import GosApi, GoContract
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.bilateral.bilateral_api import BilateralApi
from energydeskapi.customers.users_api import UsersApi
from moneyed import EUR
import pandas as pd
from energydeskapi.customers.customers_api import CustomersApi
from energydeskapi.lems.lems_api import LemsApi
from energydeskapi.geolocation.location_api import LocationApi
from energydeskapi.types.location_enum_types import LocationTypeEnum
from datetime import datetime, timedelta
from energydeskapi.sdk.datetime_utils import convert_loc_datetime_to_utcstr
from energydeskapi.types.contract_enum_types import ContractStatusEnum, GosEnergySources
from energydeskapi.types.market_enum_types import CommodityTypeEnum, InstrumentTypeEnum, MarketEnum
from energydeskapi.sdk.money_utils import FormattedMoney
import json
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])

from energydeskapi.examples.tradingbook_samples import query_trading_books


def get_contract_profile(api_conn):
    js=BilateralApi.get_contract_profile(api_conn,6153, "Yearly")
    print(js)

def get_fixedprice_contracts(api_conn):
    #query_trading_books(api_conn)
    df=ContractsApi.list_contracts_df(api_conn, {"trading_book":29, "page_size":100})
    print(df)
    contract_id=df['external_contract_id'].iloc[0]
    print(contract_id)
    contract_id="HEV_FASTPRIS_117"
    #tex=LemsApi.get_contract_doc(api_conn,str(contract_id))
    tex_file = BilateralApi.get_contract_doc(api_conn,str(contract_id))
    print(tex_file)
if __name__ == '__main__':
    api_conn=init_api()
    get_fixedprice_contracts(api_conn)
