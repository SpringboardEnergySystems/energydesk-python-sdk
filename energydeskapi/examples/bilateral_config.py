import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.bilateral.bilateral_api import RatesConfigurations, CurvesConfigurations, BilateralApi
import pandas as pd
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def list_configurations(api_conn):

   res=BilateralApi.get_rates_configurations(api_conn)
   print(res[0])
   res=BilateralApi.get_curve_configurations(api_conn)
   print(res)
   #CurvesConfigurations

def create_configurations(api_conn):
   rr=CurvesConfigurations()
   print(rr.get_dict())
   rr.description="NO1 test"
   rr.price_area="NO1"
   rr.basic_curve_model="PRICEIT"
   BilateralApi.upsert_curve_configuration(api_conn, rr)

def update_configurations(api_conn):
   rr=RatesConfigurations(0.061, 0.02)
   print(rr.get_dict(api_conn))
   rr.description="TEST"
   rr.pk=1
   BilateralApi.upsert_rates_configuration(api_conn, rr)

if __name__ == '__main__':
    api_conn=init_api()

    list_configurations(api_conn)

