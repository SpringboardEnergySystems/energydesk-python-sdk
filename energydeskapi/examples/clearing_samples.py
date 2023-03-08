
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

def fetch_clearing_report_records(api_conn):
    df = ClearingApi.get_clearing_report_records(api_conn)
    print(df)

def fetch_embedded_clearing_report_records(api_conn):
    filter = {"clearing_report_type": ClearingReportTypeEnum.ACCMVALUE.value,
              "clearing_date__gte": "2022-10-09",
              "clearing_date__lte": "2022-10-10"}
    df = ClearingApi.get_clearing_report_records_embedded(api_conn, filter)
    print(df)

def fetch_clearing_reports(api_conn):
    df=ClearingApi.get_clearing_reports(api_conn)
    print(df)

def fetch_embedded_clearing_reports(api_conn):
    filter = {"clearing_report_type": ClearingReportTypeEnum.DELIVERY.value}
    res=ClearingApi.get_clearing_reports_embedded(api_conn, filter)
    for rec in res['results']:
        print(rec['pk'], rec['clearing_report_type']['description'])
    #print(res)

def fetch_clearing_report_types(api_conn):
    df=ClearingApi.get_clearing_report_types(api_conn)
    print(df)

def reconcile_contracts(api_conn):
    date = "2023-03-01"
    result = ClearingApi.perform_reconciliation(api_conn, date)
    print(result)


if __name__ == '__main__':

    api_conn=init_api()
    #fetch_clearing_reports(api_conn)
    #fetch_embedded_clearing_reports(api_conn)
    #fetch_clearing_report_records(api_conn)
    #fetch_embedded_clearing_report_records(api_conn)
    #fetch_clearing_report_types(api_conn)
    #test_clearing_data(api_conn)
    reconcile_contracts(api_conn)
