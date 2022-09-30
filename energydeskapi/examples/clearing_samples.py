import sys

import requests
import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.clearing.clearing_api import ClearingApi
from energydeskapi.types.clearing_enum_types import ClearingReportTypeEnum

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def test_clearing_data(api_conn):
    ClearingApi.query_clearing_report_data(api_conn, 711, ClearingReportTypeEnum.TRANSACTIONS, "2021-01-01", "2023-01-01")

def fetch_clearing_reports(api_conn):
    df=ClearingApi.get_clearing_reports(api_conn)
    print(df)

def fetch_clearing_report_types(api_conn):
    df=ClearingApi.get_clearing_report_types(api_conn)
    print(df)


if __name__ == '__main__':

    api_conn=init_api()
    #fetch_clearing_reports(api_conn)
    #fetch_clearing_report_types(api_conn)
    test_clearing_data(api_conn)
