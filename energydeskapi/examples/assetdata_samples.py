import logging

import pandas as pd

from energydeskapi.assets.assets_api import AssetsApi, AssetSubType, Asset, AssetTechData
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.types.asset_enum_types import AssetTypeEnum
from energydeskapi.sdk.common_utils import init_api

from datetime import datetime, timedelta
from energydeskapi.types.asset_enum_types import AssetForecastAdjustEnum
import json
from energydeskapi.assetdata.assetdata_api import AssetDataApi, TimeSeriesAdjustments, TimeSeriesAdjustment
from energydeskapi.types.asset_enum_types import AssetForecastAdjustEnum
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def add_expressions(api_conn, asset_desc):
    jsondata = AssetsApi.get_assets(api_conn, {'extern_asset_id':asset_desc})
    asset=jsondata['results'][0]
    print(asset['pk'])
    tas=TimeSeriesAdjustments()
    tas.asset_pk=asset['pk']
    tas.is_active_for_asset=True
    tas.time_series_type_pk=2
    ta=TimeSeriesAdjustment()
    ta.description="Rebate"
    ta.adjustment_type_pk=AssetForecastAdjustEnum.PERCENTAGE.value
    ta.value=0.94
    ta.denomination_type_pk=1
    tas.adjustments.append(ta)
    AssetDataApi.upsert_timeseries_adjustments(api_conn, tas)

def query_asset_info(api_conn, asset_pk_list):
    res = AssetDataApi.get_assetgroup_forecast(api_conn,{'asset_id_in':asset_pk_list})
    df=pd.DataFrame(data=json.loads(res))
    df.index=df['timestamp']
    df.index=pd.to_datetime(df.index)
    df=df.tz_convert("Europe/Oslo")
    df['timestamp']=df.index
    print(df)

def demo_data(api_conn):
    curr=datetime.today().strftime(("%Y-%m-%d"))
    next = (datetime.today() + timedelta(days=1000)).strftime(("%Y-%m-%d"))
    tss = TimeSeriesAdjustments()
    tss.is_active_for_asset=True
    tss.asset_pk=5

    ts=TimeSeriesAdjustment()
    ts.description="Base rebate"
    ts.value=0.95
    ts.adjustment_type_pk=AssetForecastAdjustEnum.PERCENTAGE.value
    ts.denomination_type_pk=1
    tss.adjustments.append(ts)


    ts=TimeSeriesAdjustment()
    ts.description = "High tax rebate"
    ts.value=0.30
    ts.period_from=curr
    ts.period_until=next
    ts.adjustment_type_pk=AssetForecastAdjustEnum.PERCENTAGE.value
    ts.denomination_type_pk=1
    tss.adjustments.append(ts)

    ts=TimeSeriesAdjustment()
    ts.description = "Option cust rebate"
    ts.value=0.70
    ts.adjustment_type_pk=AssetForecastAdjustEnum.EUROP_OPTION.value
    ts.denomination_type_pk=2
    tss.adjustments.append(ts)

    print(tss.get_dict())

    lst_expressions=[]
    ta=TimeSeriesAdjustment(0,description="Base Rebate",adjustment_type_pk=AssetForecastAdjustEnum.PERCENTAGE.value, denomination="Prc", value=0.94,value2=0,period_from=None,period_until=None )
    lst_expressions.append(ta)
    ta=TimeSeriesAdjustment(0,description="High tax",adjustment_type_pk=AssetForecastAdjustEnum.PERCENTAGE.value, denomination="Prc",value= 0.7,value2=0,period_from=dtFrom,period_until=dtUntil )
    lst_expressions.append(ta)
    tas=TimeSeriesAdjustments(pk=0,asset_pk=0,time_series_type_pk=1,is_active_for_asset=True, lst_expressions=lst_expressions)
    AssetDataApi.upsert_timeseries_adjustments(api_conn, tas)

    print(AssetDataApi.get_timeseries_adjustment_types(api_conn))

if __name__ == '__main__':

    api_conn = init_api()
    #query_asset_info(api_conn, [98])
    add_expressions(api_conn, "08-Trepellets")
    #print(AssetDataApi.get_timeseries_adjustments(api_conn))
    #print(AssetDataApi.get_timeseries_adjustment_types(api_conn))
    #print(AssetDataApi.get_timeseries_adjustment_denomination_types(api_conn))

