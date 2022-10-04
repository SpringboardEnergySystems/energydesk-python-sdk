import logging
from energydeskapi.contracts.contracts_api import ContractsApi, Contract
from energydeskapi.sdk.common_utils import init_api
from moneyed import EUR
from datetime import datetime, timedelta
from energydeskapi.sdk.datetime_utils import convert_datime_to_utcstr, convert_datime_to_locstr
from energydeskapi.types.contract_enum_types import ContractStatusEnum, ContractTypeEnum
from energydeskapi.types.market_enum_types import CommodityTypeEnum, InstrumentTypeEnum
from energydeskapi.sdk.money_utils import FormattedMoney
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def get_contract_types(api_conn):
    df=ContractsApi.list_commodity_types(api_conn)
    print(df)
    df=ContractsApi.list_instrument_types(api_conn)
    print(df)
    df=ContractsApi.list_contract_types(api_conn)
    print(df)
    df=ContractsApi.list_contract_statuses(api_conn)
    print(df)

def register_sample_contract(api_conn):
    yester = (datetime.today() + timedelta(days=-1)).replace( hour=0, minute=0, second=0, microsecond=0)
    dtstr1=convert_datime_to_utcstr(yester)
    dtstr2=convert_datime_to_locstr(yester, "Europe/Oslo")  #In order to get the date correct
    #trading_book = 1  # Use lookup function to set correct trading book key. Server will check if user allowed still
    contract_type = ContractTypeEnum.FINANCIAL
    commodity_type = CommodityTypeEnum.POWER
    contract_status = ContractStatusEnum.REGISTERED
    instrument_type = InstrumentTypeEnum.FWD
    trading_book=2
    company = 2
    trader=2
    c=Contract("EXT ID SAMPLE 667",
               trading_book,
               FormattedMoney(55.30, EUR),5,
               FormattedMoney(2.1, EUR),
               FormattedMoney(2.0, EUR),
               dtstr2[0:10],dtstr1,
               contract_type,
               commodity_type,
               instrument_type,
               contract_status,
               "SELL",
               company,
               company,
               trader)
    res=ContractsApi.upsert_contract(api_conn, c)
    print(res)

def query_paginated_contracts(api_conn):
    parameters={}
    parameters['contract_type']=3
    head={'Authorization': 'Token 0a60f84e67763bb3214b4b1bfad522d2f947a4f3'}
    import requests
    fullurl="http://127.0.0.1:8001/api/portfoliomanager/contracts/"
    result = requests.get(fullurl, headers=head, params=parameters)
    print(result)
    #ContractsApi.list_contracts(api_conn, parameters)

if __name__ == '__main__':
    api_conn=init_api()
    register_sample_contract(api_conn)
