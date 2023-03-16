from datetime import date, datetime, timedelta

import pandas as pd
from dateutil.relativedelta import relativedelta
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

def fetch_clearing_report_records(api_conn, report_type_enum, days_back):
    from_date = datetime.today() - relativedelta(days=days_back)
    until_date = datetime.today()
    print(from_date.strftime("%Y-%m-%d"))
    print(until_date.strftime("%Y-%m-%d"))
    filter = {"clearing_report_type": report_type_enum.value,
              "clearing_date__gte": from_date.strftime("%Y-%m-%d"),
              "clearing_date__lte": until_date.strftime("%Y-%m-%d")}
    json_data = ClearingApi.get_clearing_report_records_embedded(api_conn, filter)
    print(json_data)
    df=pd.DataFrame(data=json_data)
    print(df.sort_values(by=['clearing_date', 'Series']))
    mask = (df['clearing_date'] >= "2023-03-09") & (df['clearing_date'] < "2023-03-10")
    df=df.loc[mask]
    print(df)

def fetch_clearing_reports(api_conn):
    df=ClearingApi.get_clearing_reports(api_conn)
    print(df)

def fetch_embedded_clearing_reports(api_conn):
    filter = {"clearing_report_type": ClearingReportTypeEnum.DELIVERY.value}
    res=ClearingApi.get_clearing_reports_embedded(api_conn, filter)
    for rec in res['results']:
        print(rec['pk'], rec['clearing_report_type']['description'])

def fetch_clearing_report_types(api_conn):
    df=ClearingApi.get_clearing_report_types(api_conn)
    print(df)

def reconcile_trades(api_conn, date):  #Performs reconciliation
    date = "2023-03-01"
    result = ClearingApi.perform_reconciliation(api_conn, date)
    print(result)

def fetch_reconciled_trades(api_conn):
    from_date = datetime.today() - relativedelta(days=2)
    until_date = datetime.today()
    param = {"clearing_date__gte": from_date,
             "clearing_date__lte": until_date}
    result = ClearingApi.get_reconciled_trades(api_conn, param)
    print(result)


if __name__ == '__main__':

    api_conn=init_api()

    fetch_clearing_report_types(api_conn)
    fetch_clearing_report_records(api_conn, ClearingReportTypeEnum.TRANSACTIONS, 12)

    #fetch_reconciled_trades(api_conn)

