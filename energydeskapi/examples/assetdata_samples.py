import logging

import pandas as pd

from energydeskapi.assets.assets_api import AssetsApi, AssetSubType, Asset, AssetTechData
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.types.asset_enum_types import TimeSeriesTypesEnum
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.types.common_enum_types import PeriodResolutionEnum
from datetime import datetime, timedelta
from energydeskapi.sdk.common_utils import key_from_url
from energydeskapi.sdk.datetime_utils import convert_datetime_from_utc
from energydeskapi.assetdata.assetdata_api import AssetDataApi, TimeSeriesAdjustments, TimeSeriesAdjustment
from energydeskapi.types.asset_enum_types import AssetForecastAdjustEnum, AssetForecastAdjustDenomEnum
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def add_expressions(api_conn, asset_desc):
    jsondata = AssetsApi.get_assets(api_conn, {'description':asset_desc})
    print(jsondata['results'])
    #sondata=json.loads(jsondata)
    asset=jsondata['results'][0]
    print(asset['pk'])
    epk = 0#asset['pk']
    description = "supertest"
    expression_type_pk = AssetForecastAdjustEnum.PERCENTAGE.value
    denomination =AssetForecastAdjustDenomEnum.PERC.value

    value ="0.67"
    value2 = None
    denomination2=None
    period_from = None
    period_until = None
    adjustments = []
    ta = TimeSeriesAdjustment(epk, description, expression_type_pk, value, denomination,  value2, denomination2,period_from,
                              period_until)
    adjustments.append(ta)
    tss = TimeSeriesAdjustments(0, asset['pk'], 1,  True, adjustments)


    success, returned_data, status_code, error_msg = AssetDataApi.upsert_timeseries_adjustments(
       api_conn, tss)
    print('XXXXX')
    print(returned_data)


def query_assetdata_types(api_conn):
    print("Adj types")
    res = AssetDataApi.get_timeseries_adjustment_types(api_conn)
    print(res)
    print("Adj denoms")
    res = AssetDataApi.get_timeseries_adjustment_denominations(api_conn)
    print(res)
def query_asset_info(api_conn, asset_pk_list):
    df = AssetDataApi.get_assetgroup_forecast_df(api_conn,asset_pk_list)
    print(df)
    #print(df.where(df.timestamp <= '2025-01-01').dropna())

    #print(df)

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


def get_date_part(isostr):
    dt=convert_datetime_from_utc(isostr)
    return dt.strftime("%Y-%m-%d")

def load_adjustments(api_conn, asset_id):
    res=AssetDataApi.get_timeseries_adjustments(api_conn, {'asset__id': asset_id})
    print("Adjustments for ", asset_id)
    ut=[]
    if res is not None and len(res)>0:
        for a in res[0]['adjustments']:
            pk = int(a['pk'])
            description=a['description']
            adjustment_type_pk=key_from_url(a['adjustment_type'])
            denomination=key_from_url(a['value_denomination'])
            value=a['value']
            value2 = None if a['value2'] is None else a['value2']
            denomination2 = None if a['value2_denomination'] is None else key_from_url(a['value2_denomination'])
            period_from = None if a['period_from'] is None else get_date_part(a['period_from'])
            period_until = None if a['period_until']is None else get_date_part(a['period_until'])
            ta = TimeSeriesAdjustment(pk,description,adjustment_type_pk,value, denomination,value2, denomination2, period_from,period_until )
            ut.append(ta    )
    print(ut)

import json
def load_assetdata(api_conn):
    #asset=AssetsApi.get_asset_url(api_conn, 1)
    assets=AssetsApi.get_assets(api_conn, {"description":"B2C"})
    print(assets)
    params={
        'asset__id':assets['results'][0]['pk'],
        'time_series_type__id':TimeSeriesTypesEnum.FORECASTS.value,
        'resolution': PeriodResolutionEnum.MONTHLY.value
    }
    res = AssetDataApi.get_aggregated_timeseries(api_conn,params)
    df=AssetDataApi.get_assetgroup_forecast_df(api_conn, [assets['results'][0]['pk']], PeriodResolutionEnum.MONTHLY)
    #jsdata=json.loads(res) if type(res)==str else res
    #df=pd.DataFrame(data=jsdata)
    print(df.plot())

def load_assetdata2(api_conn):
    #asset=AssetsApi.get_asset_url(api_conn, 1)
    assets=AssetsApi.get_assets(api_conn)
    print(assets)
    params={
        'assetlist_id__in':[assets['results'][0]['pk']],
        'time_series_type__id':TimeSeriesTypesEnum.METERREADINGS.value,
        'resolution': PeriodResolutionEnum.HOURLY.value
    }

    df=AssetDataApi.get_asset_timeseries(api_conn, params)
    df=pd.DataFrame(data=eval(df))
    # if df is not None and len(df)>0:
    #     df1=df
    #     df1.index = df.index.tz_convert(None)
    #     #df1['timestamp']= df['timestamp'].tz_convert(None)
    #     #df1['date'] = df['date'].tz_convert(None)
    #     #df1['dates_shift'] = df['dates_shift'].tz_convert(None)
    #     print(df1)
    #     df1.ioc[:, 4:].to_excel("./output.xlsx")
    #     df = df.iloc[:, 4:]
    print(df)

if __name__ == '__main__':

    api_conn = init_api()
    #add_expressions(api_conn, "Asset group - B2C")
    #query_assetdata_types(api_conn)
    #pd.set_option('display.max_rows', None)
    load_assetdata(api_conn)
    #load_adjustments(api_conn, [4])
    #print(AssetDataApi.get_timeseries_adjustments(api_conn))
    #print(AssetDataApi.get_timeseries_adjustment_types(api_conn))
    #print(AssetDataApi.get_timeseries_adjustment_denomination_types(api_conn))

