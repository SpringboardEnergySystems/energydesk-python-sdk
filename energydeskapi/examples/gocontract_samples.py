import logging
import logging
from energydeskapi.contracts.contracts_api import ContractsApi, Contract, ContractFilter, ContractTag
from energydeskapi.contracts.dealcapture import bilateral_dealcapture
from energydeskapi.contracts.masteragreement_api import MasterAgreementApi, MasterContractAgreement
from energydeskapi.gos.gos_api import GosApi, GoContract
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.customers.users_api import UsersApi
from moneyed import EUR
import pandas as pd
from energydeskapi.customers.customers_api import CustomersApi
from energydeskapi.contracts.masteragreement_api import MasterContractAgreement
from energydeskapi.geolocation.location_api import LocationApi
from energydeskapi.types.location_enum_types import LocationTypeEnum
from datetime import datetime, timedelta
from energydeskapi.sdk.datetime_utils import convert_loc_datetime_to_utcstr
from energydeskapi.types.contract_enum_types import ContractStatusEnum, GosEnergySources
from energydeskapi.types.market_enum_types import CommodityTypeEnum, InstrumentTypeEnum, MarketEnum
from energydeskapi.sdk.money_utils import FormattedMoney
import json
from energydeskapi.gos.gos_api import GosApi, GoContract
from energydeskapi.gos.gos_utils import generate_default_gofields, generate_default_gocontract
from energydeskapi.sdk.common_utils import init_api
from datetime import datetime, timedelta
from dateutil import parser
import json
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])



def gen_default_contract(api_conn):
    deliv=datetime.today()
    c=generate_default_gocontract(api_conn)
    cf=generate_default_gofields(asset_pk=1, delivery_date=None)
    c.certificates.append(cf)
    print(c.get_dict(api_conn))
def get_sample_contract(api_conn, commodity):
    yester = (datetime.today() + timedelta(days=-1)).replace( hour=0, minute=0, second=0, microsecond=0)
    dtstr1=convert_loc_datetime_to_utcstr(yester)
    dtstr2=convert_loc_datetime_to_utcstr(yester, "Europe/Oslo")  #In order to get the date correct
    #trading_book = 1  # Use lookup function to set correct trading book key. Server will check if user allowed still

    commodity_type = commodity
    contract_status = ContractStatusEnum.APPROVED
    instrument_type = InstrumentTypeEnum.FWD
    trading_book=2
    company = 2
    trader=2
    c=Contract("EXT ID SAMPLE GO1234",
               trading_book,
               FormattedMoney(232.30, EUR),5,
               FormattedMoney(2.1, EUR),
               FormattedMoney(2.0, EUR),
               dtstr2[0:10],dtstr1,
               commodity_type,
               instrument_type,
               contract_status,
               "SELL",
               company,
               MarketEnum.GOs_MARKET,
               trader)

    return c

def register_testdata(api_conn):
    def initialize_certificates(api_conn, certs):
        for c in certs:
            res = GosApi.register_certificate(api_conn, c, c)

        rr = GosApi.get_certificates(api_conn)
        print(rr)

    initialize_certificates(api_conn, ['super green', 'not so green'])
def query_source_data(api_conn):
    parameters_dict={}
    parameters_dict['undelying_source'] = 2
    go_contr = GosApi.get_source_data(api_conn, parameters_dict)
    #print(json.dumps(go_contr, indent=2))

def query_contracts(api_conn):
    parameters_dict={}
    parameters_dict['undelying_source'] = 2
    go_contr = GosApi.get_contracts_embedded(api_conn, {})
    print(json.dumps(go_contr, indent=2))

def query_sources(api_conn):
    x=GosApi.get_source_collections_embedded(api_conn)
    print(json.dumps(x, indent=2))
if __name__ == '__main__':
    api_conn=init_api()
    gen_default_contract(api_conn)
    #query_sources(api_conn)

