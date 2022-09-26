import logging
from energydeskapi.contracts.contracts_api import ContractsApi
from energydeskapi.sdk.common_utils import init_api

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
    query_paginated_contracts(api_conn)
