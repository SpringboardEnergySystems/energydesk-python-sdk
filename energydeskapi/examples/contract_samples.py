import logging
from energydeskapi.contracts.contracts_api import ContractsApi, Contract
from energydeskapi.gos.gos_api import GosApi, GoContract
from energydeskapi.sdk.common_utils import init_api
from moneyed import EUR
from energydeskapi.geolocation.location_api import LocationApi
from energydeskapi.types.location_enum_types import LocationTypeEnum
from datetime import datetime, timedelta
from energydeskapi.sdk.datetime_utils import convert_datime_to_utcstr, convert_datime_to_locstr
from energydeskapi.types.contract_enum_types import ContractStatusEnum, ContractTypeEnum, GosEnergySources
from energydeskapi.types.market_enum_types import CommodityTypeEnum, InstrumentTypeEnum, MarketEnum
from energydeskapi.sdk.money_utils import FormattedMoney
import json
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

def get_sample_contract(api_conn, commodity):
    yester = (datetime.today() + timedelta(days=-1)).replace( hour=0, minute=0, second=0, microsecond=0)
    dtstr1=convert_datime_to_utcstr(yester)
    dtstr2=convert_datime_to_locstr(yester, "Europe/Oslo")  #In order to get the date correct
    #trading_book = 1  # Use lookup function to set correct trading book key. Server will check if user allowed still
    contract_type = ContractTypeEnum.FINANCIAL
    commodity_type = commodity
    contract_status = ContractStatusEnum.APPROVED
    instrument_type = InstrumentTypeEnum.FWD
    trading_book=2
    company = 2
    trader=2
    c=Contract("EXT ID SAMPLE 137312381263",
               trading_book,
               FormattedMoney(232.30, EUR),5,
               FormattedMoney(2.1, EUR),
               FormattedMoney(2.0, EUR),
               dtstr2[0:10],dtstr1,
               contract_type,
               commodity_type,
               instrument_type,
               contract_status,
               "SELL",
               company,
               MarketEnum.NORDIC_POWER,
               trader)

    return c

def register_normal_contract(api_conn):
    deliv_start = (datetime.today() + timedelta(days=100)).replace(hour=0, minute=0, second=0, microsecond=0)
    deliv_end = (datetime.today() + timedelta(days=400)).replace(hour=0, minute=0, second=0, microsecond=0)
    main_contract=get_sample_contract(api_conn, CommodityTypeEnum.POWER)
    main_contract.commodity_delivery_from=deliv_start
    main_contract.commodity_delivery_until=deliv_end
    main_contract.product_code="ODD-PROD2022"

    #print(main_contract.get_dict(api_conn))
    import json
    print(json.dumps(main_contract.get_dict(api_conn), indent=2))
    return ContractsApi.upsert_contract(api_conn, main_contract)
def register_sample_contract(api_conn):
    deliv_start = (datetime.today() + timedelta(days=100)).replace(hour=0, minute=0, second=0, microsecond=0)
    deliv_end = (datetime.today() + timedelta(days=400)).replace(hour=0, minute=0, second=0, microsecond=0)
    main_contract=get_sample_contract(api_conn, CommodityTypeEnum.GOs)
    main_contract.product_delivery_from=deliv_start
    main_contract.product_delivery_until=deliv_end

    res = LocationApi.get_local_areas(api_conn, LocationTypeEnum.GOs_OFFER_AREA)
    go_contract=GoContract()
    go_contract.main_contract=main_contract
    cert=GosApi.get_certificate_by_key(api_conn,4)
    go_contract.certificates.append(cert)
    go_contract.energy_source=GosApi.get_energysource_by_key(api_conn, GosEnergySources.HYDRO)
    go_contract.underlying_source=LocationApi.get_local_area_url(api_conn, res[3]['pk'])
    go_contract.invoice_with_mva=False
    go_contract.extra_info="blablabla"
    go_contract.invoice_date= convert_datime_to_utcstr(deliv_start)[:10]
    go_contract.delivery_date = convert_datime_to_utcstr(deliv_start)[:10]


    print(go_contract.get_dict(api_conn))
    GosApi.upsert_contract(api_conn, go_contract)
import pandas as pd
def load_contracts(api_conn):
    res=GosApi.get_contracts(api_conn, {'page_size':30})
    print(res)
    df=pd.DataFrame(res)
    print(df)
def test_gos(api_conn):
    #res=GosApi.register_certificate(api_conn, "Bl¨ått valg", "Et test cert")
    #print(res)
    rr=GosApi.get_contracts(api_conn)
    print(rr)
def query_paginated_contracts(api_conn):
    parameters={}
    parameters['contract_type']=3
    head={'Authorization': 'Token 0a60f84e67763bb3214b4b1bfad522d2f947a4f3'}
    import requests
    fullurl="http://127.0.0.1:8001/api/portfoliomanager/contracts/"
    result = requests.get(fullurl, headers=head, params=parameters)
    print(result)
    #ContractsApi.list_contracts(api_conn, parameters)
def query_sources(api_conn):
    x=GosApi.get_source_collections(api_conn)
    #print(x)
    x=GosApi.get_source_data(api_conn)

    print(json.dumps(json.loads(x), indent=2))
if __name__ == '__main__':
    api_conn=init_api()
    load_contracts(api_conn)
