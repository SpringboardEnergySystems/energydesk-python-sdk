import json
import logging
import geopandas as gpd
from pandas.core.interchange import column

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


import pytz, pendulum
from energydeskapi.sdk.pandas_utils import convert_date_column
def get_contracts(api_conn):
    jsondata = DwhApi.get_contract_dimension( api_conn, {})
    #print(json.dumps(jsondata, indent=2))
    df=pd.DataFrame(jsondata)
    print(df)
def get_reports(api_conn):
    jsondata = DwhApi.get_report_dimension( api_conn, {"currency":"NOK","report_type":"MONTHLY_PNL"})
    #print(json.dumps(jsondata, indent=2))
    df=pd.DataFrame(jsondata)
    df['report_date'] = df.apply(convert_date_column, axis=1, args=("report_date",))
    report_dates=[str(d)[:10] for d in df['report_date'].unique()]
    print(report_dates)


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

def get_gridexposure(api_conn):
    param = {'report_type': "GRIDNODE_RISK", 'portfolio_id': 15}
    jsondata = DwhApi.get_grid_exposure( api_conn, param)
    #print(json.dumps(jsondata, indent=2))
    #df=pd.DataFrame(json.loads(jsondata['gridexposuremap']))
    df = gpd.GeoDataFrame.from_features(json.loads(jsondata['gridexposuremap']))
    df2 = pd.DataFrame(jsondata['gridexposureview'])

    print(df)
    print(df2)
def get_report_types(api_conn):
    jsondata = DwhApi.get_report_dimension( api_conn, {})
    print(json.dumps(jsondata, indent=2))
    #df=pd.DataFrame(jsondata)
    #print(df)


def load_specific_reports(api_conn, report_type, portfolio_id):
    print("LOADING" ,report_type)
    param={'report_type':report_type,'portfolio_id':portfolio_id, 'currency':'EUR', 'report_date':'2025-05-26T22:00:00Z'}
    jsondata = DwhApi.get_periodview_timeseries( api_conn, param)
    df=pd.DataFrame(jsondata)
    return df
def load_reports(api_conn):
    df_powerexpo=load_specific_reports(api_conn, 'PERIODVIEW_CONTRACTS_MONTHLY', 36)
    print(df_powerexpo)


def get_flex_reports(api_conn):
    param={'report_type':'FLEXIBILITY_ACTIVATION_DELIVERY'}
    jsondata = DwhApi.get_flexibility_activations( api_conn, param)
    df=pd.DataFrame(jsondata)
    print(df)
    df.to_excel("./flexhandler.xlsx")

if __name__ == '__main__':

    api_conn = init_api()
    #get_report_types(api_conn)
    load_reports(api_conn)

