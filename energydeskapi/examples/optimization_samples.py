import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.energydesk.general_api import GeneralApi
from energydeskapi.optimization.battery_optimizer_api import BatteryOptimizationApi, OptimizerInput

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])




def optimize_battery(api_conn):
    indata=OptimizerInput()
    BatteryOptimizationApi.optimize_battery(api_conn, indata)




if __name__ == '__main__':

    api_conn=init_api()
    optimize_battery(api_conn)
