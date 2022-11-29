import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.lems.lems_api import LemsApi, LocalProduct
import pandas as pd
import pytz
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

def check_create_product(api_conn, price_area, product):
    res = LocationApi.get_local_areas(api_conn)
    loc_url=None
    for loc in res:
        if loc['title']==price_area:
            loc_url=LocationApi.get_local_area_url(api_conn,loc['pk'])
            break
    if loc_url is None:
        logger.error("No area found in system matching " + price_area)
    print("Products belong to location ", loc_url)
    usrprofile = UsersApi.get_user_profile(api_conn)
    print("Logged in user is ",usrprofile)
    comp=CustomersApi.get_company_from_registry_number(api_conn,usrprofile['company_nbr'])
    cmop_url=CustomersApi.get_company_url(api_conn, comp['pk'])
    print("Company url ", cmop_url)
    markets = LemsApi.get_local_markets(api_conn)#, "Fixed price market", cmop_url, locations)
    mark=None
    for m in markets:
        if m['description']=='Fixed price market':
            mark=m
            break
    if mark is None:
        logger.error("No market defined for fixed price products")
    markurl=LemsApi.get_local_market_url(api_conn, mark['pk'])
    print("Market url is ", markurl)

    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

    #ticker = "FWD" + price_area + "-" + str(year) + "YR-" + month_name + str(first_day.year)[2:]
    locprod = LocalProduct()
    locprod.ticker = product['name']
    locprod.currency = "NOK"
    locprod.local_market = markurl
    locprod.traded_from = today
    locprod.traded_until = product['period_from']
    locprod.local_area = loc_url
    locprod.description = "Fixed price contract " + product['name']
    locprod.area = price_area
    locprod.commodity_delivery_from = product['period_from']
    locprod.commodity_delivery_until = product['period_until']
    locprod.market = MarketEnum.NORDIC_POWER
    locprod.commodity_type = CommodityTypeEnum.POWER
    locprod.instrument_type = InstrumentTypeEnum.FWD
    locprod.commodity_profile={'monthly_profile':product['monthly_profile'],
    'weekday_profile':product['weekday_profile'],
    'daily_profile':product['daily_profile']}
    print(locprod.commodity_profile)
    print(locprod.get_dict(api_conn))
    #Check and create product if not already on server. User must av admin rights
    #LemsApi.upsert_localproduct(api_conn, locprod)

def set_timezone(locdt, loczone="Europe/Oslo"):
    norzone = pytz.timezone(loczone)
    d_aware = locdt.astimezone(norzone)
    return d_aware
def define_products(price_area):
    period_from=set_timezone(datetime(2023,1,1))

    period_until_3yr=(period_from + relativedelta(years=3))
    period_until_7yr=(period_from + relativedelta(years=7))
    products=[]
    # Baseload
    p1={'name': 'FWD' + price_area + '-3YR-JAN23',
        'period_from':period_from,
        'period_until':period_until_3yr,
        'contract_type':"BASELOAD",
        'monthly_profile':get_month_list(), #All months
        'weekday_profile':get_weekdays_list(),
        'daily_profile':list(range(24))} #All weekdays
    products.append(p1)

    # Baseload 7year
    p1b={'name': 'FWD' + price_area + '-BASE-7YRJAN23',
        'period_from':period_from,
        'period_until':period_until_7yr,
        'contract_type':"BASELOAD",
        'monthly_profile':get_month_list(),
        'weekday_profile':get_weekdays_list(),
        'daily_profile':list(range(24))
        }
    products.append(p1b)

    # Winter Workweek
    p2={'name': 'FWD' + price_area + '-WINTERWEEK-3YRJAN23',
        'period_from':period_from,
        'period_until':period_until_3yr,
        'contract_type':"PROFILE",
        'monthly_profile':get_winter_profile(),
        'weekday_profile':get_workweek(),
        'daily_profile':list(range(24))
        }
        
    products.append(p2)

    # Winter Weekend
    p3={'name': 'FWD' + price_area + '-WINTERWEEKEND-3YRJAN23',
        'period_from':period_from,
        'period_until':period_until_3yr,
        'contract_type':"PROFILE",
        'monthly_profile':get_winter_profile(),
        'weekday_profile':get_weekend(),
        'daily_profile':list(range(24))}
    products.append(p3)
    df_products=pd.DataFrame(data=products)
    return products

if __name__ == '__main__':
    #pd.set_option('display.max_rows', None)
    api_conn = init_api(dirname(__file__))
    price_area="NO1"
    products=define_products(price_area)
    for p in products:
        check_create_product(api_conn=api_conn, price_area=price_area, product=p)

