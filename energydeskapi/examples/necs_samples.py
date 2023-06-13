import logging

import pandas as pd

from energydeskapi.sdk.common_utils import init_api
from energydeskapi.necs.necs_api import NecsApi

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])

def fetch_necs_certificates(api_conn):
    result = NecsApi.get_necs_certificates(api_conn)
    print(result)

def fetch_necs_certificate_by_key(api_conn):
    pk = 2
    result = NecsApi.get_necs_certificate_by_key(api_conn, pk)
    print(result)

def fetch_necs_transactions(api_conn):
    result = NecsApi.get_necs_transactions(api_conn)
    print(result)

def fetch_necs_transaction_by_key(api_conn):
    pk = 4
    result = NecsApi.get_necs_transaction_by_key(api_conn, pk)
    print(result)

def fetch_necs_transaction_bundles(api_conn):
    result = NecsApi.get_necs_transaction_bundles(api_conn)
    print(result)

def fetch_necs_transaction_bundles_by_key(api_conn):
    pk = 3
    result = NecsApi.get_necs_transaction_bundle_by_key(api_conn, pk)
    print(result)


def fetch_necs_proddevice_versions(api_conn):
    pk = 3
    result = NecsApi.get_necs_production_device_versions(api_conn)
    df=pd.DataFrame(data=result)
    print(df.columns)
    print(df.sort_values(by="licence_expiry"))

if __name__ == '__main__':
    pd.set_option('display.max_rows', None)
    api_conn = init_api()
    #fetch_necs_certificates(api_conn)
    #fetch_necs_certificate_by_key(api_conn)
    #fetch_necs_transactions(api_conn)
    #fetch_necs_transaction_by_key(api_conn)
    fetch_necs_proddevice_versions(api_conn)
    #fetch_necs_transaction_bundles_by_key(api_conn)
