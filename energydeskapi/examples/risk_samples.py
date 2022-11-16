import sys
import requests
import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.risk.risk_api import RiskApi

import json

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])

def calc_volats(api_conn):
    df=RiskApi.calc_volatilities_df(api_conn, 12, ['NO1', 'NO2'])
    print(df)


if __name__ == '__main__':

    api_conn=init_api()
    calc_volats(api_conn)

