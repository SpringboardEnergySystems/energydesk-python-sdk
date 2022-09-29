import sys

import requests
import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.clearing.clearing_api import ClearingApi

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def fetch_clearing_reports(api_conn):
    df=ClearingApi.get_clearing_reports(api_conn)
    print(df)

def fetch_clearing_report_types(api_conn):
    df=ClearingApi.get_clearing_report_types(api_conn)
    print(df)


if __name__ == '__main__':

    api_conn=init_api()
    fetch_clearing_reports(api_conn)
    fetch_clearing_report_types(api_conn)
