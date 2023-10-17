import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.energydesk.general_api import GeneralApi
from energydeskapi.optimization.battery_optimizer_api import BatteryOptimizationApi, OptimizerInput
import pendulum
import json
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])




def optimize_battery(api_conn):
    indata=OptimizerInput()
    #from_time = serializers.DateTimeField(help_text=("Optimize From Time"))
    #until_time = serializers.DateTimeField(help_text=("Optimize Until Time"))
    #customer_profile= serializers.IntegerField(help_text=("Customer Profile TYpe"))
    #yearly_kwh = serializers.FloatField(help_text=("Yearly Consumption KWh"))

    #battery_capacity_kwh = serializers.FloatField(help_text=("Battery Capacity KWh"))
    ##battery_charging_power_kw = serializers.FloatField(help_text=("Discharging Power KW"))
    #battery_dicharging_power_kw = serializers.FloatField(help_text=("Discharging Power KW"))
    indata.optimize_fromdate=pendulum.today().subtract(months=3)
    indata.optimize_untildate=pendulum.today().subtract(months=1)
    indata.capacity_kwh=100
    indata.charging_power_kw=5
    indata.dis_charging_power_kw=5

    success, json_res, status_code, error_msg=BatteryOptimizationApi.optimize_battery(api_conn, indata)

    d=json.loads(json_res)

    print(json.dumps(d, indent=2))




if __name__ == '__main__':

    api_conn=init_api()
    optimize_battery(api_conn)
