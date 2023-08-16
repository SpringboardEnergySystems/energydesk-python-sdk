from datetime import date, datetime, timedelta

import pandas as pd
from dateutil.relativedelta import relativedelta
import logging
from dateutil import parser
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

def fetch_riskarray_info(api_conn):

    filter = {"clearing_report_type": ClearingReportTypeEnum.SPAN_PARAM_CONTRACTINFOLIST.value}
    res=ClearingApi.get_clearing_report_records(api_conn, filter)
    df=pd.DataFrame(data=res)

    filter = {"clearing_report_type": ClearingReportTypeEnum.SPAN_PARAM_RISKARRAYSLIST.value}
    res=ClearingApi.get_clearing_report_records(api_conn, filter)
    df2=pd.DataFrame(data=res)
    risk_ticker_map={}
    risk_clearingdate_map = {}
    for index,row in df.iterrows():
        isin=row['isin_code']
        ticker=row['ticker']
        valid=False
        if ticker.find("SYAL")>=0 or ticker.find("SYOS")>=0:
            valid=True
        if ticker.find("ENOM") >= 0 or ticker.find("ENOW") >= 0 \
                or ticker.find("ENOYR") >= 0 or ticker.find("ENOQ") >= 0:
            valid = True
        if valid==False:
            continue
        risk_ticker_map[ticker] ={}
        deliver_from = parser.isoparse(row['first_delivery_date'])
        deliver_until = parser.isoparse(row['last_delivery_date'])
        target=df2.loc[df2['contract_id'] == isin]
        risk_ticker_map[ticker]['deliver_from']=deliver_from
        risk_ticker_map[ticker]['deliver_until'] = deliver_until
        risk_ticker_map[ticker]['clearing_date']=[]
        for i in range(0, len(target['clearing_date'].values)):
            cldate = target['clearing_date'].values[i]
            if cldate not in risk_clearingdate_map:
                risk_clearingdate_map[cldate]={}
            base=float(target['base_price'].values[i])/10000
            scenarios=[]
            for j in range(1,17, 2):
                scenarios.append(float(target['value_change_' + str(j)].values[i])/100)
            scenarios.append(float(target['value_change_16'].values[i]) / 100)
            risk_clearingdate_map[cldate][ticker]={'delivery_from':deliver_from,
            'delivery_until':deliver_until,'base':base, 'scenarios':scenarios}
            risk_ticker_map[ticker]['clearing_date'].append({'clearing_date':cldate,'base':base, 'scenarios':scenarios})

    k=list(risk_clearingdate_map.keys())[0]

    print(k, risk_clearingdate_map[k])



if __name__ == '__main__':

    api_conn=init_api()

    fetch_riskarray_info(api_conn)
    #fetch_clearing_report_records(api_conn, ClearingReportTypeEnum.TRANSACTIONS, 12)

    #fetch_reconciled_trades(api_conn)

