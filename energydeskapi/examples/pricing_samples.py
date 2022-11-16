import sys
import requests
import logging
from datetime import datetime
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.pricing.pricing_api import PricingApi

import json

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])

def calc_collars(api_conn):
    price_area="NO1"
    currency="NOK"
    price_min=40
    price_max=200
    date_from=datetime.today()
    number_of_months=12
    interest_rate=0.02
    volatility=0.3
    df=PricingApi.calc_collars(api_conn,price_area,currency,price_min, price_max, date_from, number_of_months, interest_rate, volatility )
    print(df)


if __name__ == '__main__':

    api_conn=init_api()
    calc_collars(api_conn)

