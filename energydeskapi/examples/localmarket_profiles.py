import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.lems.lems_api import LemsApi, LocalProductProfile
import pandas as pd
import pytz
from energydeskapi.types.market_enum_types import DeliveryTypeEnum
from os.path import join, dirname
from energydeskapi.customers.users_api import UsersApi
from energydeskapi.customers.customers_api import CustomersApi
from energydeskapi.geolocation.location_api import LocationApi
from energydeskapi.types.market_enum_types import CommodityTypeEnum, InstrumentTypeEnum, MarketEnum
from energydeskapi.types.market_enum_types import CommodityTypeEnum, InstrumentTypeEnum
from datetime import datetime
import logging
from energydeskapi.sdk.common_utils import init_api
from datetime import datetime
from dateutil.relativedelta import relativedelta
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.types.common_enum_types import get_month_list,get_weekdays_list
from energydeskapi.sdk.pandas_utils import get_winter_profile, get_workweek, get_weekend
logger = logging.getLogger(__name__)

def list_current_profiles(api_conn):
    profs=LemsApi.get_product_profiles(api_conn)
    print(profs)
def retrieve_product_profiles(api_conn, pk):
    profs=LemsApi.get_profile_by_key(api_conn, pk)
    print(profs)

def check_create_profile(api_conn, profile):

    locprod = LocalProductProfile()
    locprod.description = profile['description']
    locprod.ticker_subname = profile['sub_ticker']
    locprod.profile_category=profile['profile_type']
    locprod.commodity_profile={'monthly_profile':profile['monthly_profile'],
    'weekday_profile':profile['weekday_profile'],
    'daily_profile':profile['daily_profile']}
    print(locprod.get_dict(api_conn))
    #Check and create product if not already on server. User must av admin rights
    LemsApi.upsert_localproductprofile(api_conn, locprod)

def set_timezone(locdt, loczone="Europe/Oslo"):
    norzone = pytz.timezone(loczone)
    d_aware = locdt.astimezone(norzone)
    return d_aware
def define_profiles():

    profiles=[]
    # Winter Workweek
    p2={'description': 'Workweek Sep-Apr',
        'sub_ticker':'WINTERWEEK',
        'profile_type':"PROFILE",
        'monthly_profile':get_winter_profile(),
        'weekday_profile':get_workweek(),
        'daily_profile':list(range(24))
        }
        
    profiles.append(p2)

    # Winter Weekend
    p3={'description': 'Weekends Sep-Apr',
        'sub_ticker': 'WINTERWEEKEND',
        'profile_type':"PROFILE",
        'monthly_profile':get_winter_profile(),
        'weekday_profile':get_weekend(),
        'daily_profile':list(range(24))}
    profiles.append(p3)

    p4={'description': 'Weekends Sep-Apr (8-17)',
        'sub_ticker': 'WINTERPEAK',
        'profile_type':"PROFILE",
        'monthly_profile':get_winter_profile(),
        'weekday_profile':get_workweek(),
        'daily_profile':list(range(8,18))}
    profiles.append(p4)
    df_products=pd.DataFrame(data=profiles)
    print(profiles)
    return profiles
import sys
if __name__ == '__main__':
    #pd.set_option('display.max_rows', None)
    api_conn=init_api()
    list_current_profiles(api_conn)
    #print("Get specific")
    #retrieve_product_profiles(api_conn, 1)
    #sys.exit(0)
    products=define_profiles()
    for p in products:
        check_create_profile(api_conn=api_conn, profile=p)

