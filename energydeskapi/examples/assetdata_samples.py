import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.assets.assetdata_api import AssetDataApi, TimeSeriesAdjustments, TimeSeriesAdjustment
from datetime import datetime, timedelta
from energydeskapi.types.asset_enum_types import AssetForecastAdjustEnum
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def query_asset_info(api_conn):
    res = AssetDataApi.get_latest_forecast(api_conn,{})
    print(res)

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
    ts.denomination="%"
    tss.adjustments.append(ts)


    ts=TimeSeriesAdjustment()
    ts.description = "High tax rebate"
    ts.value=0.30
    ts.period_from=curr
    ts.period_until=next
    ts.adjustment_type_pk=AssetForecastAdjustEnum.PERCENTAGE.value
    ts.denomination="%"
    tss.adjustments.append(ts)

    ts=TimeSeriesAdjustment()
    ts.description = "Option cust rebate"
    ts.value=0.70
    ts.adjustment_type_pk=AssetForecastAdjustEnum.EUROP_OPTION.value
    ts.denomination="NOK strike"
    tss.adjustments.append(ts)

    print(tss.get_dict())

    print(AssetDataApi.get_timeseries_adjustment_types(api_conn))

if __name__ == '__main__':

    api_conn = init_api()
    print(AssetDataApi.get_timeseries_adjustments(api_conn))
    print(AssetDataApi.get_timeseries_adjustment_types(api_conn))
    print(AssetDataApi.get_timeseries_adjustment_denomination_types(api_conn))

