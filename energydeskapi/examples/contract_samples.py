import logging
from energydeskapi.contracts.contracts_api import ContractsApi, Contract, ContractFilter
from energydeskapi.contracts.dealcapture import bilateral_dealcapture
from energydeskapi.contracts.masteragreement_api import MasterAgreementApi, MasterContractAgreement
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

def get_contract_filters(api_conn):
    parameter = {"user": 1}
    json_contractfilters = ContractsApi.get_contract_filters(api_conn, parameter)
    print(json_contractfilters)

def get_contract_filter_pk(api_conn):
    pk = 1
    json_contractfilter = ContractsApi.get_contract_filter_by_key(api_conn, pk)
    print(json_contractfilter)

def get_master_contract_agreement(api_conn):
    parameter = {"user": 1}
    json_contractfilters = MasterAgreementApi.get_master_agreement(api_conn)
    print(json_contractfilters)

def register_contract_filters(api_conn):
    contract_filter = ContractFilter()
    contract_filter.pk = 4
    contract_filter.user = "http://127.0.0.1:8001/api/customers/profiles/1/"
    contract_filter.description = "filkters"
    contract_filter.filters = "filterds"
    success, returned_data, status_code, error_msg = ContractsApi.upsert_contract_filters(api_conn, contract_filter)
    print(returned_data)

def register_master_contract_agreement(api_conn):
    master_agreement = MasterContractAgreement()
    master_agreement.pk = "4"
    master_agreement.title = "title"
    master_agreement.created_at = "2022-12-01T08:29:46.594Z"
    master_agreement.contract_owner = "http://127.0.0.1:8001/api/customers/companies/721/"
    master_agreement.counterpart = "http://127.0.0.1:8001/api/customers/companies/721/"
    master_agreement.contract_info_1 = "contract_info11111"
    master_agreement.contract_info_2 = "contract_info"
    master_agreement.contract_info_3 = "contract_info"
    master_agreement.signed_contract_url_ref = "url"
    MasterAgreementApi.upsert_master_agreement(api_conn, master_agreement)

def get_sample_contract(api_conn, commodity):
    yester = (datetime.today() + timedelta(days=-1)).replace( hour=0, minute=0, second=0, microsecond=0)
    dtstr1=convert_datime_to_utcstr(yester)
    dtstr2=convert_datime_to_locstr(yester, "Europe/Oslo")  #In order to get the date correct
    #trading_book = 1  # Use lookup function to set correct trading book key. Server will check if user allowed still

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
    head={'Authorization': 'Token 0a60f84e67763bb3214b4b1bfad522d2f947a4f3'}
    import requests
    fullurl="http://127.0.0.1:8001/api/portfoliomanager/contracts/"
    result = requests.get(fullurl, headers=head, params=parameters)
    print(result)
    #ContractsApi.list_contracts(api_conn, parameters)
def query_sources(api_conn):
    x=GosApi.get_source_collections_embedded(api_conn)
    #x=json.loads(x)
    #x=GosApi.get_source_data(api_conn)

    print(json.dumps(x, indent=2))
if __name__ == '__main__':
    api_conn=init_api()
    #query_sources(api_conn)
    #get_contract_filters(api_conn)
    get_contract_filter_pk(api_conn)
    #register_contract_filters(api_conn)
    #bilateral_dealcapture(api_conn)
    #get_master_contract_agreement(api_conn)
    #register_master_contract_agreement(api_conn)
