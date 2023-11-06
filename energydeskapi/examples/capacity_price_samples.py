import logging
from datetime import datetime, date
import pandas as pd
import json
from dateutil import parser
from dateutil.relativedelta import relativedelta
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.bilateral.capacity_api import CapacityApi
from energydeskapi.types.common_enum_types import PeriodResolutionEnum
from energydeskapi.lems.lems_api import LemsApi
from energydeskapi.profiles.profiles_api import ProfilesApi, StoredProfile
from energydeskapi.sdk.pandas_utils import make_empty_timeseries_df
import sys
from energydeskapi.sdk.profiles_utils import get_baseload_weekdays, get_baseload_dailyhours, get_flat_months,\
get_default_profile_months

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])

def load_current_offers(api_conn):
    current_active_priceoffers = CapacityApi.list_active_price_offers(api_conn)
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

def get_capacity_config(api_conn, asset_pk=1):
    params={"grid_component__id": asset_pk}
    jsond=CapacityApi.get_capacity_request(api_conn, params)
    print(jsond)
    return jsond[0]['requested_profile']
def create_save_profile(api_conn):
    months=get_flat_months()   # Returns 1 for each month, so easy to adjust a couple of them
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

def calculate_price(api_conn, requested_profile):
    thismonth = date.today().replace(day=1)
    dt_from = thismonth + relativedelta(months=3)
    print(dt_from, thismonth)

    dt_until = (dt_from + relativedelta(months=5)).strftime("%Y-%m-%d")
    dt_from = dt_from.strftime("%Y-%m-%d")
    df_offer=make_empty_timeseries_df(dt_from,dt_until, "H","Europe/Oslo" )
    df_offer['offered_hour']=1
    df_offer['timestamp']=df_offer.index
    print(df_offer)
    grid_component_id=1
    activation_price=4000
    offer=json.loads(df_offer.to_json(orient='records',date_format='iso'))
    success, json_res, status_code, error_msg =CapacityApi.calculate_capacity_price_externals(api_conn,
                                     grid_component_id, offer, 100, activation_price, "NOK")
    if success:
        print(json_res)
        price_offer_id=json_res['priceoffer_id']
        price = json_res['availability_price']

        CapacityApi.add_order_from_capacityoffer_id(api_conn, price_offer_id, "SELL", 5000)

    else:
        print("Error occured when calculating price")
        print(error_msg)
        price=0
    return price_offer_id, price

def enter_order_from_priceoffer(api_conn, priceoffer_id, yearly_kwh):
    # This order entry places a limit order at the price given in the offer, with validity time equal to the price offer (can be cancelled)
    success, json_res, status_code, error_msg =FixedPriceApi.add_order_from_priceoffer_id(api_conn, priceoffer_id, "BUY",  yearly_kwh)
    if not success:
        return False, error_msg, None
    return True, json_res['order_id'], json_res['ticker']

def get_orders(api_conn):
    #df = LemsApi.query_active_anonymous_orders(api_conn)
    #print(df)
    off=CapacityApi.list_active_capacity_offers(api_conn)
    for o in off:
        print(o['priceoffer_data'].keys())
        print(o.keys())
        print(o['is_still_valid'])
        print(o['company_offered']['name'])
    return None

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
    off=CapacityApi.list_active_capacity_offers(api_conn)
    print(off)
    return df



if __name__ == '__main__':

    api_conn=init_api()
    #requested_profile=get_capacity_config(api_conn)
    own_orders = LemsApi.query_own_orders(api_conn, False)
    print(own_orders)
    #priceoffer_id, price=calculate_price(api_conn, requested_profile)

    #get_orders(api_conn)
    sys.exit(0)

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

