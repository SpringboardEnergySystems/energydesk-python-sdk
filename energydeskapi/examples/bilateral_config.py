import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.bilateral.bilateral_api import RatesConfigurations, CurvesConfigurations, BilateralApi
import pandas as pd
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def create_configurations(api_conn):
   rr=RatesConfigurations(0.061, 0.02)
   print(rr.get_dict(api_conn))
   rr.description="TEST"
   BilateralApi.upsert_rates_configuration(api_conn, rr)

if __name__ == '__main__':
    api_conn=init_api()

    create_configurations(api_conn)

