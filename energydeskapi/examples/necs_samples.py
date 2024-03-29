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
    df = pd.DataFrame(data=result)
    df = df.astype({'volume': 'float'})
    df=df[['production_device_name', 'issued_date', 'volume']]
    df['key'] = df.groupby(['production_device_name', 'issued_date']).cumcount()
    df = df.pivot_table(index=['key', 'issued_date'], columns='production_device_name', values='volume', aggfunc='sum').reset_index()
    df=df.drop(columns=['key'])
    df = df.fillna(value=0)
    df=df.groupby(['issued_date']).sum()
    import numpy as np
    df=df.sort_values(by="issued_date", ascending=False)
    df.loc[:, 'Total'] = df.sum(axis=1, numeric_only=True)
    df.loc['Grand Total', :] = df.sum(axis=0)
    df = df.iloc[np.arange(-1, len(df) - 1)]
    print(df)


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
    result = NecsApi.get_necs_transaction_bundles(api_conn, {'page_size':10000})
    #print(result)
    df = pd.DataFrame(data=result)
    print(df.sort_values(by="completion_date")[['completion_date', 'transaction_volume']])
    df = df.astype({'transaction_volume': 'float', 'volume': 'float'})
    df2 = df.groupby(by=['production_device_id'], dropna=False).agg({'completion_date':'max','transaction_volume':sum, 'volume':sum})
    print(df2)

def fetch_necs_transaction_bundles_by_key(api_conn):
    pk = 3
    result = NecsApi.get_necs_transaction_bundle_by_key(api_conn, pk)
    print(result)


def fetch_necs_proddevice_versions(api_conn):
    result = NecsApi.get_necs_production_device_versions(api_conn)
    df=pd.DataFrame(data=result)
    print(df.columns)
    #print(df.sort_values(by="licence_expiry"))

if __name__ == '__main__':
    #pd.set_option('display.max_rows', None)
    api_conn = init_api()
    fetch_necs_certificates(api_conn)
    #fetch_necs_certificate_by_key(api_conn)
    #fetch_necs_transactions(api_conn)
    #fetch_necs_transaction_by_key(api_conn)
    #fetch_necs_proddevice_versions(api_conn)
    #fetch_necs_transaction_bundles(api_conn)
