import ast
import logging
from energydeskapi.contracts.contracts_api import ContractsApi, Contract, ContractFilter, ContractTag
from energydeskapi.contracts.dealcapture import bilateral_dealcapture
from energydeskapi.contracts.masteragreement_api import MasterAgreementApi, MasterContractAgreement
from energydeskapi.gos.gos_api import GosApi, GoContract
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.customers.users_api import UsersApi
from energydeskapi.sdk.money_utils import FormattedMoney, Money, CurrencyCode, gen_json_money, gen_money_from_json
import pandas as pd
from energydeskapi.customers.customers_api import CustomersApi
from energydeskapi.contracts.masteragreement_api import MasterContractAgreement
from energydeskapi.geolocation.location_api import LocationApi
from energydeskapi.types.location_enum_types import LocationTypeEnum
from datetime import datetime, timedelta
from energydeskapi.sdk.datetime_utils import convert_loc_datetime_to_utcstr
from energydeskapi.types.contract_enum_types import ContractStatusEnum
from energydeskapi.types.market_enum_types import CommodityTypeEnum, InstrumentTypeEnum, MarketEnum
from energydeskapi.sdk.money_utils import FormattedMoney
import json
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def get_contract_types(api_conn):
    df=ContractsApi.get_contract_types(api_conn, {"no_pagination": True})
    print(df)

def get_contract_filters(api_conn):
    parameter = {"page_size": 100}
    #json_contractfilters = ContractsApi.get_contract_filters(api_conn, parameter)
    from energydeskapi.marketdata.markets_api import MarketsApi
    x=MarketsApi.get_instrument_types(api_conn)
    print(x)


def get_contract_filter_pk(api_conn):
    pk = 1
    json_contractfilter = ContractsApi.get_contract_filter_by_key(api_conn, pk)
    print(json_contractfilter)

def get_contracts(api_conn, trading_book=None):
    filter={"portfolio":2}#"pk": [1,3]}
    json_data = ContractsApi.list_contracts_embedded(api_conn,filter)
    #records=json_data['results']  # 200 at a time
    for rec in json_data['results']:
        if rec['commodity']['product_code'].startswith("SYOSL"):
            print(json.dumps(rec, indent=2))
    #df=pd.DataFrame(data=eval(records))
    #print(df)

def get_contract_tags(api_conn):
    json_contractfilter = ContractsApi.get_contract_tags(api_conn)
    print(json_contractfilter)


def register_contract_tag(api_conn):
    contract_tag = ContractTag()
    contract_tag.tagname = "tag_name"
    contract_tag.description = "description"
    contract_tag.is_active = True
    success, returned_data, status_code, error_msg = ContractsApi.upsert_contract_tag(api_conn,contract_tag)
    print(returned_data)

def get_master_contract_agreements(api_conn):
    parameter = {"user": 1}
    json_masteragreement = MasterAgreementApi.get_master_agreements_embedded(api_conn)
    print(json_masteragreement)

def get_master_contract_agreement_by_pk(api_conn):
    pk = 2
    json_masteragreement = MasterAgreementApi.get_master_agreements_by_key(api_conn, pk)
    #print(json_masteragreement)

def register_contract_filters(api_conn):
    contract_filter = ContractFilter()
    contract_filter.pk = 0
    contract_filter.user = "http://127.0.0.1:8001/api/customers/profiles/1/"
    contract_filter.description = "filkters"
    contract_filter.filters = "filterds"
    success, returned_data, status_code, error_msg = ContractsApi.upsert_contract_filters(api_conn, contract_filter)
    print(returned_data)

def fix_error_message(err):
    err=err.replace("[ErrorDetail(string=", "{'msg':")
    err = err.replace("code=", "'code':")
    err = err.replace(")]", "}")

    return err


def register_master_contract_agreement(api_conn, regnmb):
    counterres=CustomersApi.get_company_from_registry_number(api_conn, regnmb)
    usrprofile=UsersApi.get_user_profile(api_conn)
    usrcomp = CustomersApi.get_company_from_registry_number(api_conn, usrprofile['company_nbr'])
    master_agreement = MasterContractAgreement()
    master_agreement.pk = 0
    master_agreement.title = "Master Agreement with " + counterres['name']
    master_agreement.created_at = datetime.today().strftime(("%Y-%m-%d"))
    master_agreement.contract_owner = None#"http://127.0.0.1:8001/api/customers/companies/" + str(usrcomp['pk']) + "/"
    master_agreement.counterpart = "http://127.0.0.1:8001/api/customers/companies/" + str(counterres['pk']) + "/"
    master_agreement.contract_info = "contract_info #1"
    master_agreement.phone = "111121111"
    master_agreement.email = "example@example.com"
    master_agreement.email_contract_documents = True
    master_agreement.signed_contract_url_ref = "http://sharepoint.com/"
    print(master_agreement.get_dict(api_conn))
    success, returned_data, status_code, error_msg=MasterAgreementApi.upsert_master_agreement(api_conn, master_agreement)
    records=json.loads(error_msg)
    for key in records:
        print(key)
        print(records[key])

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
    c=Contract("EXT ID SAMPLE 137312381263",
               trading_book,
               FormattedMoney(232.30, CurrencyCode.EUR),5,
               FormattedMoney(2.1, CurrencyCode.EUR),
               FormattedMoney(2.0, CurrencyCode.EUR),
               dtstr2[0:10],dtstr1,
               commodity_type,
               instrument_type,
               contract_status,
               "SELL",
               company,
               MarketEnum.NORDIC_POWER,
               trader)

    return c

def list_master_agreements(api_conn):
    rets=MasterAgreementApi.get_master_agreements_embedded(api_conn)
    print(rets)

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
    go_contract.invoice_date= convert_loc_datetime_to_utcstr(deliv_start)[:10]
    go_contract.delivery_date = convert_loc_datetime_to_utcstr(deliv_start)[:10]


    print(go_contract.get_dict(api_conn))
    GosApi.upsert_contract(api_conn, go_contract)
import pandas as pd
def load_contracts(api_conn):
    res=ContractsApi.list_contracts_embedded(api_conn)
    print(json.dumps(res, indent=2))

def load_contracts_csv(api_conn):
    data=ContractsApi.list_contracts_csv(api_conn, {'portfolio_id':13})
    print(data)

def load_contracts_emir(api_conn):
    data=ContractsApi.list_contracts_emir(api_conn, {'portfolio_id':13})
    print(data)

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
def currcontr(api_conn):
    res=ContractsApi.list_contracts_compact(api_conn,
                                        {"page_size": 100, "commodity__commodity_type": CommodityTypeEnum.CURRENCY.value})
    df=pd.DataFrame(json.loads(res['results']))
    print(df)

def load_contract(api_conn, contract_key=2128):
    res = ContractsApi.get_contract(api_conn,
                                                  contract_pk=contract_key)
    print(res)
from energydeskapi.sdk.common_utils import key_from_url
def cancel_contract(api_conn, contract_key=37125):
    contract = ContractsApi.get_contract(api_conn,contract_pk=contract_key)
    if contract is None:
        print("Not founc")
        return None
    contract['external_contract_id'] = contract_key
    contract['contract_status'] = ContractsApi.get_contract_status_url(api_conn, ContractStatusEnum.CANCELLED.value)
    if contract['commodity']['commodity_profile'] is None:
        contract['commodity']['commodity_profile'] = {}
    if contract['contract_status_comment'] is None:
        contract['contract_status_comment'] = ''
    if contract['contract_profile'] is None:
        contract['contract_profile'] = ""
    success, returned_data, status_code, error_msg = ContractsApi.upsert_contract_from_dict(
            api_conn, contract)
    print(status_code)
def get_fixedprice_contracts(api_conn):
    records=ContractsApi.list_contracts_compact(api_conn, {"trading_book":29, "page_size":100})
    print(records)
    for rec in json.loads(records['results']):
        if rec['external_id']=="HEV_FASTPRIS_117":
            print(json.dumps(rec, indent=2))
if __name__ == '__main__':
    api_conn=init_api()
    #get_contract_filters(api_conn)
    #load_contracts_csv(api_conn)
    cancel_contract(api_conn)
    #get_contract_filters(api_conn)
    #get_contract_filter_pk(api_conn)
    #register_contract_filters(api_conn)
    #bilateral_dealcapture(api_conn)
    #get_contract_tags(api_conn)
    #get_contract_types(api_conn)
    #register_master_contract_agreement(api_conn,"982584027")
    #register_contract_tag(api_conn)
    #register_master_contract_agreement(api_conn, "922675163")
    #register_master_contract_agreement(api_conn, "819449392")
