import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.assetdata.assetdata_api import AssetDataApi
from energydeskapi.energydesk.general_api import GeneralApi
from energydeskapi.optimization.battery_optimizer_api import BatteryOptimizationApi, OptimizerInput
from energydeskapi.optimization.flexibility_optimizer_api import FlexibilityOptimizationApi
import pendulum
import pandas as pd
import json
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def optimize_assets(api_conn):
    param={}
    param['period_from']=str(pendulum.today(tz="Europe/Oslo").subtract(days=500))[0:10]
    param['period_until']=str(pendulum.today(tz="Europe/Oslo").subtract(days=1))[0:10]
    param['assets']=['707057500032174572', '707057500032140638']

    success, json_res, status_code, error_msg=AssetDataApi.calculate_maxusage(api_conn, param)
    df_max=pd.DataFrame(json_res['assetdata'])
    print(df_max)
    sum_max=df_max['fuse_size'].sum()
    print("Optimize under ", sum_max)
    param['period_from'] = str(pendulum.today(tz="Europe/Oslo").subtract(days=100))[0:10]
    param['tot_capacity_limit'] = sum_max
    FlexibilityOptimizationApi.optimize_flexibility(api_conn, param)




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
    optimize_assets(api_conn)
