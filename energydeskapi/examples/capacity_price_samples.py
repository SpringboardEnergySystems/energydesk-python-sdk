import logging
from datetime import datetime, date
import pandas as pd
import json
from dateutil import parser
from dateutil.relativedelta import relativedelta
from energydeskapi.sdk.common_utils import key_from_url
from energydeskapi.customers.customers_api import CustomersApi, Company
from energydeskapi.customers.users_api import UsersApi, User, UserGroup, UserFeatureAccess
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.bilateral.capacity_api import CapacityApi
from energydeskapi.types.common_enum_types import PeriodResolutionEnum
from energydeskapi.lems.lems_api import LemsApi
from energydeskapi.profiles.profiles_api import ProfilesApi, StoredProfile
from energydeskapi.sdk.pandas_utils import make_empty_timeseries_df
import sys
from energydeskapi.sdk.profiles_utils import get_baseload_weekdays, get_baseload_dailyhours, get_flat_months,\
get_default_profile_months
from energydeskapi.sdk.profiles_utils import get_zero_profile,get_baseload_weekdays, get_baseload_dailyhours, get_baseload_months
import pandas as pd
from energydeskapi.bilateral.capacity_api import CapacityApi, AvailabilityTender, AvailableHours
from energydeskapi.assets.assets_api import AssetsApi
from energydeskapi.types.asset_enum_types import AssetCategoryEnum
import pendulum

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])

def test_capacity_config(api_conn):
    params={"grid_asset_id": 1,
            "period_from": str(pendulum.datetime(2024,1,1, tz="Europe/Oslo")),
            "period_until": str(pendulum.datetime(2024,1,12, tz="Europe/Oslo"))}
    jsond=CapacityApi.get_capacity_profile(api_conn, params)
    print(jsond)


def load_tender(api_conn, idx):
    jsondata=CapacityApi.get_capacity_request_embedded(api_conn)
    if len(jsondata)==0:
        return None
    return jsondata[idx]


def load_capacity_requests(api_conn):
    jsondata=CapacityApi.get_capacity_request_embedded(api_conn)
    cap_info=[]
    for j in jsondata:
        if j['description'] is None:
            continue
        rec={'pk':j['pk'],'description':j['description'],'asset':j['grid_component']['description'],
             'request': str(j['grid_component']['description']) + " (" + str(j['description']) + ")"}
        print(j)
        cap_info.append(rec)
    df=pd.DataFrame(data=cap_info)
    print(df)
    #print(json.dumps(jsondata, indent=2))
    return jsondata
def save_availability_hours(api_conn):
    usrprofile = UsersApi.get_user_profile(api_conn)
    comp=CustomersApi.get_company_from_registry_number(api_conn, usrprofile['company_nbr'])
    my_comp=comp['pk']
    for req in load_capacity_requests(api_conn):
        #grid=key_from_url(req['grid_component'])
        period_from = req['period_from']
        period_until = req['period_until']
        t1=pendulum.parse(period_from, tz="Europe/Oslo")
        t2=t1.add(months=1)
        print(t1, t2)
        df_availability_hours = make_empty_timeseries_df(t1, t2, "H", "Europe/Oslo")
        df_availability_hours['offered_hour'] = 1
        df_availability_hours['timestamp'] = df_availability_hours.index
        print(df_availability_hours)
        ga=AvailableHours()
        ga.period_from=str(t1)
        ga.period_until = str(t2)
        ga.availability=df_availability_hours.to_json(orient='records')
        ga.request_response_pk=req['pk']
        ga.company_pk=my_comp
        #print(ga.get_dict(api_conn))
        CapacityApi.upsert_availability_hours(api_conn, ga)



def register_capacity_requests(api_conn):
    params={"asset_category":AssetCategoryEnum.GRID_COMPONENT.value,"page_size":100}
    assets=AssetsApi.get_assets_embedded(api_conn, params)
    for ass in assets['results']:
        cap=AvailabilityTender()
        cap.description="Euroflex Q1-24"
        cap.activation_addon=3000
        cap.grid_component=ass['pk']
        cap.availability_period_from=str(pendulum.datetime(2024,1,1, tz="Europe/Oslo"))
        cap.availability_period_until = str(pendulum.datetime(2024, 3, 1, tz="Europe/Oslo"))
        prof=get_zero_profile()
        prof["monthly_profile"]['January']=1
        prof["monthly_profile"]['February'] = 1
        prof["monthly_profile"]['March'] = 0.5
        prof["weekday_profile"]['Monday'] = 0.3
        prof["weekday_profile"]['Tuesday'] = 0.3
        prof["weekday_profile"]['Wednesday'] = 1.0
        prof["weekday_profile"]['Thursday'] = 1.0
        prof["weekday_profile"]['Friday'] = 0.9
        prof["weekday_profile"]['Saturday'] = 0.5
        prof["weekday_profile"]['Sunday'] = 0.5
        for i in range(15,19):
            prof["daily_profile"][i] = 1.0
        for i in range(7,10):
            prof["daily_profile"][i] = 1.0
        cap.requested_hours = prof
        print(cap.requested_hours)
        CapacityApi.upsert_capacity_request(api_conn,cap)

    return dict

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



def calculate_capacity_price(api_conn):
    tender=load_tender(api_conn,1)
    if tender is None:
        return
    tender_id=tender['pk']
    price_addon=3000
    activation_price=4700

    success, json_res, status_code, error_msg =CapacityApi.calculate_capacity_price(api_conn,
                                     tender_id,price_addon,activation_price, "NOK")
    if success:
        #print(json_res)
        df=pd.DataFrame(data=json_res['calculation_result']['pricing_details'])
        print(df[df['option_premium']!=0])
        print(df)
    else:
        print("Error occured when calculating price")
        print(error_msg)
        price=0


def calculate_price_as_customer(api_conn):
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
    register_capacity_requests(api_conn)
    get_current_own_orders(api_conn)
    #register_capacity_requests(api_conn)
    #calculate_capacity_price(api_conn)
    #calculate_price_as_customer(api_conn)
    #save_availability_hours(api_conn)
    #requested_profile=get_capacity_config(api_conn)
    #own_orders = LemsApi.query_own_orders(api_conn, False)
    #print(own_orders)
    #priceoffer_id, price=calculate_price(api_conn)

    #get_orders(api_conn)
    #sys.exit(0)
