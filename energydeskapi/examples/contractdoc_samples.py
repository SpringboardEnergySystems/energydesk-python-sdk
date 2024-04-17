import logging
from energydeskapi.contracts.contracts_api import ContractsApi, Contract, ContractFilter, ContractTag
from energydeskapi.contracts.dealcapture import bilateral_dealcapture
from energydeskapi.contracts.masteragreement_api import MasterAgreementApi, MasterContractAgreement
from energydeskapi.gos.gos_api import GosApi, GoContract
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.bilateral.bilateral_api import BilateralApi

import json
from energydeskapi.sdk.pandas_utils import make_empty_timeseries_df
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
    #df=ContractsApi.list_contracts_df(api_conn, {"trading_book":29, "page_size":100})
    #print(df)
    #contract_id=df['external_contract_id'].iloc[0]
    #print(contract_id)
    contract_id="HEV_FASTPRIS_117"
    #tex=LemsApi.get_contract_doc(api_conn,str(contract_id))
    tex_file = BilateralApi.get_contract_doc(api_conn,str(contract_id))
    print(tex_file)
import pendulum
def get_preview_of_capacity_contract(api_conn):
    df_offer = make_empty_timeseries_df(pendulum.datetime(2024,1,15, tz="Europe/Oslo"),
                                        pendulum.datetime(2024,2,15, tz="Europe/Oslo"),
                                        "H", "Europe/Oslo")
    df_offer['timestamp']=df_offer.index
    df_offer['offered_hour']=1
    preview_payload={
        'tender_id':"122",
        'meterpoint_id':'770577777333333',
        'email': 'owner@customer.no',
        'company_registry_number': '925971855',
        'reserved_capacity': 1.5,
        'offered_hours': df_offer.to_json(orient="records",date_format='iso')
    }
    tex_file =BilateralApi.preview_capacity_contract_doc(api_conn, preview_payload)
    print(tex_file)
    #query_trading_books(api_conn)
    #df=ContractsApi.list_contracts_df(api_conn, {"trading_book":29, "page_size":100})
    #print(df)
    #contract_id=df['external_contract_id'].iloc[0]
    #print(contract_id)
    contract_id="HEV_FASTPRIS_117"
    #tex=LemsApi.get_contract_doc(api_conn,str(contract_id))
    #tex_file = BilateralApi.get_contract_doc(api_conn,str(contract_id))
    #print(tex_file)

def get_flexibility_contracts(api_conn):

    contract_id="ELVIA_TILGJENGELIGHET_001"
    #tex=LemsApi.get_contract_doc(api_conn,str(contract_id))
    tex_file = BilateralApi.get_contract_doc(api_conn,str(contract_id))
    print(tex_file)
if __name__ == '__main__':
    api_conn=init_api()
    get_preview_of_capacity_contract(api_conn)
