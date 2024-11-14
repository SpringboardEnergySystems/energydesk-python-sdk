import json
import logging
from energydeskapi.system.default_asset_types import initialize_default_etrm_assettypes
from energydeskapi.audit.audit_log_api import AuditLogApi
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.types.asset_enum_types import AssetCategoryEnum
import pandas as pd
from energydeskapi.dwh.dwh_api import DwhApi
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])



def get_contracts(api_conn):
    jsondata = DwhApi.get_contract_dimension( api_conn, {})
    #print(json.dumps(jsondata, indent=2))
    df=pd.DataFrame(jsondata)
    print(df)
def get_reports(api_conn):
    jsondata = DwhApi.get_report_dimension( api_conn, {})
    #print(json.dumps(jsondata, indent=2))
    df=pd.DataFrame(jsondata)
    print(df)
def get_contract_timeseries(api_conn):
    jsondata = DwhApi.get_contract_timeseries( api_conn, {})
    #print(json.dumps(jsondata, indent=2))
    df=pd.DataFrame(jsondata)
    print(df)
def get_periodview_timeseries(api_conn):
    jsondata = DwhApi.get_periodview_timeseries( api_conn, {})
    #print(json.dumps(jsondata, indent=2))
    df=pd.DataFrame(jsondata)
    print(df)
def get_report_types(api_conn):
    jsondata = DwhApi.get_report_dimension( api_conn, {})
    #print(json.dumps(jsondata, indent=2))
    df=pd.DataFrame(jsondata)
    print(df)


def load_specific_reports(api_conn, report_type, portfolio_id):
    print("LOADING" ,report_type)
    param={'report_type':report_type,'portfolio_id':portfolio_id}
    jsondata = DwhApi.get_periodview_timeseries( api_conn, param)
    df=pd.DataFrame(jsondata)
    return df
def load_reports(api_conn):
    #df_pnl = load_specific_reports(api_conn, "MONTHLY_PNL")
    #df_pnl2 = df_pnl.pivot(index='period_from', columns='portfolio', values=['realized', 'unrealized'])
    #df_pnl2=df_pnl2.fillna(0)
    #print(df_pnl2)

    df_powerexpo=load_specific_reports(api_conn, 'POWER_EXPOSURE', 14)
    print(df_powerexpo)
    df_priceexpo = load_specific_reports(api_conn, 'PRICE_EXPOSURE', 14)
    print(df_priceexpo)
    df_netfuel = load_specific_reports(api_conn, 'NET_BIOBRENSEL', 14)
    print(df_netfuel)
    df_netpowerexpo = load_specific_reports(api_conn, 'NET_POWER_EXPOSURE', 14)
    print(df_netpowerexpo)

if __name__ == '__main__':

    api_conn = init_api()
    #get_report_types(api_conn)
    load_reports(api_conn)

