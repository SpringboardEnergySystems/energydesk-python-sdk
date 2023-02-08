import logging
from datetime import datetime, date
import pandas as pd
from dateutil import parser
from dateutil.relativedelta import relativedelta
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.bilateral.fixed_price_api import FixedPriceApi

from energydeskapi.sdk.profiles_utils import get_baseload_weekdays, get_baseload_dailyhours, get_baseload_months

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])

def load_current_offers(api_conn):
    current_active_priceoffers = FixedPriceApi.list_active_price_offers(api_conn)
    print(current_active_priceoffers)
    if len(current_active_priceoffers)>0:
        return current_active_priceoffers[0]
    return None

def calculate_price(api_conn):
    thismonth = date.today().replace(day=1)
    expiry = date.today() + relativedelta(days=3)
    dt_from = (thismonth + relativedelta(month=3))
    dt_until = (dt_from + relativedelta(years=2)).strftime("%Y-%m-%d")
    dt_from = dt_from.strftime("%Y-%m-%d")
    print("Calculate price for ", dt_from, dt_until)
    price_area="NO1"
    months=get_baseload_months()
    months['January'] = 8
    months['February'] = 8
    months['March'] = 4
    months['October'] = 4
    months['November'] = 8
    months['December'] = 8
    print(months)
    weekdays=get_baseload_weekdays()
    hours=get_baseload_dailyhours()
    profile_name="Winterprofile"

    success, json_res, status_code, error_msg =FixedPriceApi.calculate_contract_price(api_conn, profile_name, dt_from, dt_until,price_area,
                                                                                      months,weekdays, hours
                                                                                      )
    if success:
        print(json_res)
        offer_id=json_res['priceoffer_id']
        # Could enter a buy order directly on this price (referring to priceoffer_id=
        #yearly_kwh=100000
        #success, json_res, status_code, error_msg =FixedPriceApi.add_order_from_priceoffer_id(api_conn, pid, "BUY", yearly_kwh)
        #print(json_res)
    else:
        print("Error occured when calculating price")
        print(error_msg)

def enter_order_from_priceoffer(api_conn, priceoffer_id, yearly_kwh):
    # This order entry places a limit order at the price given in the offer, with validity time equal to the price offer (can be cancelled)
    success, json_res, status_code, error_msg =FixedPriceApi.add_order_from_priceoffer_id(api_conn, priceoffer_id, "BUY",  yearly_kwh)
    print(json_res)

if __name__ == '__main__':

    api_conn=init_api()
    # Calculates a price for a give  profile. It will expire at the end of the week, but current active offers can also be returned on the
    # next call: load_current_offers
    # Use priceoffer_id to input a Buy order with a given KWh/year volume.
    #calculate_price(api_conn)
    most_recent=load_current_offers(api_conn)
    print("Most recent price offer ",most_recent['priceoffer_id'], most_recent['priceoffer_data']['price'] )
    #enter_order_from_priceoffer(api_conn, most_recent['priceoffer_id'], 125000)

