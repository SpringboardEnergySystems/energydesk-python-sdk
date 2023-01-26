import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.lems.lems_api import LemsApi, CustomProfile
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
    profs=LemsApi.get_custom_profiles(api_conn)
    print(profs)



def check_create_profile(api_conn, profile):

    locprod =CustomProfile()
    locprod.price_area = profile['price_area']
    locprod.delivery_from = profile['delivery_from']
    locprod.delivery_until=profile['delivery_until']
    locprod.volume_profile={'monthly_profile':profile['volume_profile']['monthly_profile'],
    'weekday_profile':profile['volume_profile']['weekday_profile'],
    'daily_profile':profile['volume_profile']['daily_profile']}
    #Check and create product if not already on server. User must av admin rights
    success, json_res, status_code, error_msg=LemsApi.upsert_custom_profile(api_conn, locprod)
    if success:
        print("Got ticker to use in order entry", json_res['ticker'])

def set_timezone(locdt, loczone="Europe/Oslo"):
    norzone = pytz.timezone(loczone)
    d_aware = locdt.astimezone(norzone)
    return d_aware

def define_custom_profiles():

    profiles=[]
    # Winter Workweek
    p2={'delivery_from': '2023-04-01',
        'delivery_until': '2026-04-01',
        'price_area':'NO1',
        'volume_profile':{'monthly_profile':get_winter_profile(),
                    'weekday_profile':get_workweek(),
                    'daily_profile':list(range(24))
                   }
        }
    profiles.append(p2)
    p2={'delivery_from': '2023-04-01',
        'delivery_until': '2026-04-01',
        'price_area':'NO5',
        'volume_profile':{'monthly_profile':get_winter_profile(),
                    'weekday_profile':get_workweek(),
                    'daily_profile':list(range(24))
                   }
        }
    profiles.append(p2)

    p2={'delivery_from': '2023-04-01',
        'delivery_until': '2028-04-01',
        'price_area':'NO5',
        'volume_profile':{'monthly_profile':get_winter_profile(),
                    'weekday_profile':get_workweek(),
                    'daily_profile':list(range(24))
                   }
        }
    profiles.append(p2)

    p2={'delivery_from': '2023-04-01',
        'delivery_until': '2028-04-01',
        'price_area':'NO5',
        'volume_profile':{'monthly_profile':get_winter_profile(),
                    'weekday_profile':get_weekend(),
                    'daily_profile':list(range(24))
                   }
        }
    profiles.append(p2)
    return profiles
import sys
if __name__ == '__main__':
    #pd.set_option('display.max_rows', None)
    api_conn=init_api()
    list_current_profiles(api_conn)
    #print("Get specific")
    #retrieve_product_profiles(api_conn, 1)
    #sys.exit(0)
    products=define_custom_profiles()
    for p in products:
        check_create_profile(api_conn=api_conn, profile=p)

