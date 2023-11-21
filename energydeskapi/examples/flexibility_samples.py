import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.energydesk.general_api import GeneralApi
from energydeskapi.flexibility.dso_api import DsoApi
import pendulum
import json
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])




def simulate_dsr(api_conn):
    res=DsoApi.simulate_dsr_value(api_conn)





if __name__ == '__main__':

    api_conn=init_api()
    simulate_dsr(api_conn)
