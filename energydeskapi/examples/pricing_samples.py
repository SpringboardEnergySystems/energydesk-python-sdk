import logging
from datetime import datetime
import pandas as pd
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.pricing.pricing_api import PricingApi


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])

def calc_collars(api_conn):
    price_area="NO1"
    currency="EUR"
    price_min=40
    price_max=200
    date_from=datetime.today()
    number_of_months=12
    interest_rate=0.02
    volatility=0.3
    success, json_res, status_code, error_msg =PricingApi.calc_collars(api_conn,price_area,currency,price_min, price_max, date_from, number_of_months, interest_rate, volatility )
    result, periods, curvedata = json_res['result'], json_res['periods'], json_res['curve']
    # df_curve = get_period_prices(price_area)
    df_curve = pd.DataFrame(data=eval(curvedata))
    df_curve.timestamp = pd.to_datetime(df_curve.timestamp)
    df_curve.index = df_curve.timestamp
    print(df_curve)


if __name__ == '__main__':

    api_conn=init_api()
    calc_collars(api_conn)

