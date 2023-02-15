import logging

from energydeskapi.gos.gos_api import GosApi, GoContract
from energydeskapi.sdk.common_utils import init_api

import json
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


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
    query_sources(api_conn)

