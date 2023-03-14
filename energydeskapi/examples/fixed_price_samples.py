import logging
from datetime import datetime, date
import pandas as pd
from dateutil import parser
from dateutil.relativedelta import relativedelta
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.bilateral.fixed_price_api import FixedPriceApi
from energydeskapi.lems.lems_api import LemsApi
from energydeskapi.profiles.profiles_api import ProfilesApi, StoredProfile
import sys
from energydeskapi.sdk.profiles_utils import get_baseload_weekdays, get_baseload_dailyhours, get_flat_months,\
get_default_profile_months

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

def load_stored_profiles(api_conn):
    existing_profiles = ProfilesApi.get_volume_profiles(api_conn)
    print(existing_profiles)
    return None

def delete_stored_profiles(api_conn, key):
    res = ProfilesApi.delete_volume_profile(api_conn, key)
    print(res)

def create_save_profile(api_conn):
    months=get_flat_months()   # Returns 1 for each month, so easy to adjust
    months['January'] = 8
    months['February'] = 8
    months['March'] = 4
    months['October'] = 4
    months['November'] = 8
    months['December'] = 8
    weekdays=get_baseload_weekdays()
    dailyhours=get_baseload_dailyhours()

    v = StoredProfile()
    v.profile = {
        'monthly_profile':months,
        'weekday_profile': weekdays,
        'daily_profile': dailyhours
    }
    v.description="Winterprofile"
    print(v.get_dict(api_conn))
    res=ProfilesApi.upsert_volume_profile(api_conn, v)
    print(res)

def enter_order_on_priceoffer(api_conn, price_offer_id,yearly_kwh=100000):
    success, json_res, status_code, error_msg =FixedPriceApi.add_order_from_priceoffer_id(api_conn, price_offer_id,
                                                                                          "BUY", yearly_kwh)
    print(json_res)

def calculate_price(api_conn, profile_type, custom_profile_key):
    thismonth = date.today().replace(day=1)
    dt_from = thismonth + relativedelta(months=3)
    print(dt_from, thismonth)
    dt_until = (dt_from + relativedelta(years=5)).strftime("%Y-%m-%d")
    dt_from = dt_from.strftime("%Y-%m-%d")
    print("Calculate price for ", dt_from, dt_until)
    price_area="NO1"
    price_offer_id=None
    price=-1
    success, json_res, status_code, error_msg =FixedPriceApi.calculate_contract_price(api_conn,
                                     dt_from, dt_until,price_area,profile_type,custom_profile_key)
    if success:
        print(json_res)
        price_offer_id=json_res['priceoffer_id']
        price = json_res['price']
    else:
        print("Error occured when calculating price")
        print(error_msg)
    return price_offer_id, price

def enter_order_from_priceoffer(api_conn, priceoffer_id, yearly_kwh):
    # This order entry places a limit order at the price given in the offer, with validity time equal to the price offer (can be cancelled)
    success, json_res, status_code, error_msg =FixedPriceApi.add_order_from_priceoffer_id(api_conn, priceoffer_id, "BUY",  yearly_kwh)
    if not success:
        return False, error_msg, None
    return True, json_res['order_id'], json_res['ticker']

def get_available_periods(api_conn):
    periods=FixedPriceApi.get_avaiable_fixprice_periods(api_conn)
    return periods

def remove_last_entered_order(api_conn, series):
    print("Removing", series['order_id'], series['ticker'])
    LemsApi.remove_order(api_conn, series['ticker'],series['order_id'])

def get_current_own_orders(api_conn):
    df=LemsApi.query_own_orders(api_conn)  #Returned as Pandas dataframe
    if df is None or len(df.index)==0:
        return None
    for index,row in df.iterrows():
        print(row['order_id'],row['ticker'],row['price'],row['quantity'])
    return df

def get_current_own_trades(api_conn):
    df=LemsApi.get_own_trades_df(api_conn)  #Returned as Pandas dataframe
    print(df)
    return df

if __name__ == '__main__':

    api_conn=init_api()
    # Calculates a price for a give  profile. It will expire at the end of the week, but current active offers can also be returned on the
    # next call: load_current_offers
    # Use priceoffer_id to input a Buy order with a given KWh/year volume.

    periods=get_available_periods(api_conn)
    print(periods)

    load_stored_profiles(api_conn)
    #delete_stored_profiles(api_conn,12)   # Will only delete objects created by company of user
    #create_and_save_profile(api_conn)

    priceoffer_id, price=calculate_price(api_conn, "BASELOAD", custom_profile_key=None)
    #priceoffer_id, price=calculate_price(api_conn, "CUSDTOM", custom_profile_key=12)  #Use key of stored profile

    #print("May enter a volume order for price offer ",priceoffer_id, ", Price=", price )
    success, order_id, ticker=enter_order_from_priceoffer(api_conn,priceoffer_id,125000)  #Yearly KWh at the current moment
    if success:
        print("Order entered successfully:",order_id, ticker)

    df_trades= get_current_own_trades(api_conn)  #Orders that have been accepted / matched by producer

    df_orders=get_current_own_orders(api_conn)
    if df_orders is not None:
        print(df_orders)  # All recent orders, cancelled or active
        df_active_orders=df_orders.loc[df_orders['order_status']=="ACTIVE"]
        #Example of deleting the last order that is active
        #if df_active_orders is not None:
        #    remove_last_entered_order(api_conn,df_active_orders.iloc[-1])

