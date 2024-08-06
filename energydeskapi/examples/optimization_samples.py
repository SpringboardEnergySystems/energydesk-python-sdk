import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.assetdata.assetdata_api import AssetDataApi
from energydeskapi.energydesk.general_api import GeneralApi
from datetime import datetime, timedelta, timezone
from energydeskapi.optimization.battery_optimizer_api import BatteryOptimizationApi, OptimizerInput
from energydeskapi.optimization.flexibility_optimizer_api import FlexibilityOptimizationApi
import pendulum
import pandas as pd
import pytz
import json
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def optimize_maxusage(api_conn):
    param={}
    param['period_from']=str(pendulum.parse("2024-05-01",tz="Europe/Oslo"))
    param['period_until']=str(pendulum.parse("2024-05-10",tz="Europe/Oslo"))
    param['assets']=[74,75]
    param['rolling_window_size'] = 8
    param['price_area'] = "DK1"
    param['optimization_criteria'] =1

    success, data, status_code, error_msg=AssetDataApi.calculate_maxupeak(api_conn, param)
    print(data)
    print("Current peak",data['maxpeak'])
    peak=data['maxpeak']
    peak=peak*0.9  # 90% of current
    print("Optimize under ", peak)

    #param['period_from'] = str(pendulum.today(tz="Europe/Oslo").subtract(days=100))[0:10]
    param['tot_capacity_limit'] = peak
    success, json_res, status_code, error_msg=FlexibilityOptimizationApi.optimize_max_usage(api_conn, param)
    df_original=pd.DataFrame(json_res['original'])
    peak_original = float(json_res['peak_original'])
    cost_original = float(json_res['cost_original'])
    sumenergy_original = float(json_res['sumenergy_original'])
    df_optimized = pd.DataFrame(json_res['optimized'])
    peak_optimized = float(json_res['peak_optimized'])
    cost_optimized = float(json_res['cost_optimized'])
    sumenergy_optimized= float(json_res['sumenergy_optimized'])
    def prepare_timestamp(df):
        df.index = df['timestamp']
        df.index = pd.to_datetime(df.index)
        active_timezone = pytz.timezone("Europe/Oslo")
        df.index = df.index.tz_convert(active_timezone)
        df['timestamp']=df.index
        return df

    df_optimized = prepare_timestamp(df_optimized)
    df_original = prepare_timestamp(df_original)

    print("Original peak {} energy {} and cost {}".format(peak_original, sumenergy_original, cost_original))
    print("Optimized peak {} energy {} and cost {}".format(peak_optimized, sumenergy_optimized, cost_optimized))


def optimize_battery(api_conn):
    indata=OptimizerInput()
    #from_time = serializers.DateTimeField(help_text=("Optimize From Time"))
    #until_time = serializers.DateTimeField(help_text=("Optimize Until Time"))
    #customer_profile= serializers.IntegerField(help_text=("Customer Profile TYpe"))
    #yearly_kwh = serializers.FloatField(help_text=("Yearly Consumption KWh"))

    #battery_capacity_kwh = serializers.FloatField(help_text=("Battery Capacity KWh"))
    ##battery_charging_power_kw = serializers.FloatField(help_text=("Discharging Power KW"))
    #battery_dicharging_power_kw = serializers.FloatField(help_text=("Discharging Power KW"))

    indata.optimize_fromdate=pendulum.today(tz="Europe/Oslo").subtract(days=40)
    indata.optimize_untildate=pendulum.today(tz="Europe/Oslo").subtract(days=33)
    indata.capacity_kwh=100
    indata.charging_power_kw=5
    indata.dis_charging_power_kw=5

    success, json_res, status_code, error_msg=BatteryOptimizationApi.optimize_battery(api_conn, indata)

    d=json.loads(json_res)

    print(json.dumps(d, indent=2))




if __name__ == '__main__':

    api_conn=init_api()
    optimize_maxusage(api_conn)
