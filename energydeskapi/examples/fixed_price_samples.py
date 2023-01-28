import logging
from datetime import datetime, date
import pandas as pd
from dateutil.relativedelta import relativedelta
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.bilateral.fixed_price_api import FixedPriceApi

from energydeskapi.sdk.profiles_utils import get_baseload_weekdays, get_baseload_dailyhours, get_baseload_months

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])

def calculate_price(api_conn):
    thismonth = date.today().replace(day=1)
    expiry = date.today() + relativedelta(days=3)
    dt_from = (thismonth + relativedelta(month=3))
    dt_until = (dt_from + relativedelta(years=2)).strftime("%Y-%m-%d")
    dt_from = dt_from.strftime("%Y-%m-%d")
    print("Calculate price for ", dt_from, dt_until)
    price_area="NO1"
    months=get_baseload_months()
    months['January'] = 0.7
    months['July']=0.4
    months['August'] = 0.4
    weekdays=get_baseload_weekdays()
    hours=get_baseload_dailyhours()

    success, json_res, status_code, error_msg =FixedPriceApi.calculate_contract_price(api_conn, dt_from, dt_until,price_area,
                                                                                      months,weekdays, hours
                                                                                      )
    if success:
        print(json_res)
        pid=json_res['priceoffer_id']
        print("Adding offer")
        success, json_res, status_code, error_msg =FixedPriceApi.add_order_from_priceoffer_id(api_conn, pid, "BUY", expiry, 25)
        print(json_res)
    else:
        print("Something went wrong")
        print(error_msg)

if __name__ == '__main__':

    api_conn=init_api()
    calculate_price(api_conn)

