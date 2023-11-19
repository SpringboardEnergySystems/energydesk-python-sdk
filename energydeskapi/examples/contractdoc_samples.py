import logging
from energydeskapi.contracts.contracts_api import ContractsApi, Contract, ContractFilter, ContractTag
from energydeskapi.contracts.dealcapture import bilateral_dealcapture
from energydeskapi.contracts.masteragreement_api import MasterAgreementApi, MasterContractAgreement
from energydeskapi.gos.gos_api import GosApi, GoContract
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.bilateral.bilateral_api import BilateralApi

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

def get_flexibility_contracts(api_conn):

    contract_id="ELVIA_TILGJENGELIGHET_001"
    #tex=LemsApi.get_contract_doc(api_conn,str(contract_id))
    tex_file = BilateralApi.get_contract_doc(api_conn,str(contract_id))
    print(tex_file)
if __name__ == '__main__':
    api_conn=init_api()
    get_flexibility_contracts(api_conn)
