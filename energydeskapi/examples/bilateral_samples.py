import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.bilateral.bilateral_api import BilateralApi
from energydeskapi.lems.lems_api import LemsApi
from datetime import datetime, timedelta
from energydeskapi.types.common_enum_types import PeriodResolutionEnum
from energydeskapi.types.common_enum_types import get_month_list,get_weekdays_list
from energydeskapi.types.fwdcurve_enum_types import FwdCurveTypesEnum
from energydeskapi.sdk.profiles_utils import get_zero_profile,get_baseload_weekdays, get_baseload_dailyhours, get_baseload_months
import pandas as pd
import pendulum

from energydeskapi.bilateral.capacity_api import CapacityApi, CapacityProfile
from energydeskapi.assets.assets_api import AssetsApi
from energydeskapi.types.asset_enum_types import AssetCategoryEnum
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

def register_test_capacity_requests(api_conn):
    params={"asset_category":AssetCategoryEnum.PRODUCTION.value,"page_size":100}
    assets=AssetsApi.get_assets_embedded(api_conn, params)
    for ass in assets['results']:
        cap=CapacityProfile()
        cap.grid_component=ass['pk']
        cap.period_from=str(pendulum.datetime(2024,1,1, tz="Europe/Oslo"))
        cap.period_until = str(pendulum.datetime(2024, 3, 1, tz="Europe/Oslo"))
        prof=get_zero_profile()

        prof["monthly_profile"]['January']=1
        prof["monthly_profile"]['February'] = 1
        prof["monthly_profile"]['March'] = 0.5
        prof["weekday_profile"]['Monday'] = 1.0
        prof["weekday_profile"]['Tuesday'] = 1.0
        prof["weekday_profile"]['Wednesday'] = 1.0
        prof["weekday_profile"]['Thursday'] = 1.0
        prof["weekday_profile"]['Friday'] = 0.9
        prof["weekday_profile"]['Saturday'] = 0.4
        prof["weekday_profile"]['Sunday'] = 0.4
        for i in range(15,19):
            prof["daily_profile"][i] = 1.0
        for i in range(7,10):
            prof["daily_profile"][i] = 1.0
        cap.requested_profile = prof
        #print(cap.get_dict(api_conn))
        CapacityApi.upsert_capacity_request(api_conn,cap)

def get_deliveries(api_conn):
    fromd="2023-01-01"
    untild = "2025-02-01"
    success, df, df_trades, status_code, error_msg=BilateralApi.calculate_deliveries_df(api_conn, fromd,untild,
                                      resolution=PeriodResolutionEnum.DAILY.value)
    df = df.drop(['period_from'], axis=1)
    #print(df_trades.columns)
    df2=df.pivot_table(index='period_from', columns=['area','counterpart'], values='netpos', aggfunc='sum')

    print(df2)

    df3=df.pivot_table(index='period_from', columns='area', values='netpos', aggfunc='sum')
    print(df3)


def get_bilateral_trades(api_conn):
    from_date=pendulum.today()
    from_date=from_date.set(month=1, day=1)
    until_date = from_date + timedelta(days=500)
    print(from_date, until_date)
    success, df_trades, status_code, error_msg = BilateralApi.get_bilateral_trades(api_conn,
                                                                                   str(from_date),str(until_date))
    print(df_trades)
def calculate_price(api_conn):
    fromd="2023-10-01"
    untild = "2024-10-01"
    periods=[["A", fromd, untild]]

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

    print(periods)
    price_date, currency_date, df_curve, cprices, cpricedet=BilateralApi.calculate_contract_price_df(api_conn,periods, "NO1", "NOK",
                                            "CUST_1",
                                         wacc=0.06, inflation=0,
                                        monthly_profile=months,
                                        weekday_profile=weekdays,
                                        hours=hours)
    print(cprices)


def calculate_capacity_price(api_conn):
    fromd=str(pendulum.parse("2024-02-01", tz="Europe/Oslo"))
    untild = str(pendulum.parse("2024-03-01", tz="Europe/Oslo"))
    periods=[["Holmlia", fromd, untild]]

    months=get_baseload_months()
    for m in months.keys():
        months[m]=0
    months['January'] = 1
    months['February'] = 0.2
    months['March'] = 1
    months['October'] = 0
    months['November'] = 0
    months['December'] = 0
    print(months)
    weekdays=get_baseload_weekdays()
    for m in weekdays.keys():
        weekdays[m]=0
    weekdays['Thursday'] = 1
    weekdays['Friday'] = 1
    weekdays['Sunday'] = 1
    hours=get_baseload_dailyhours()
    for m in hours.keys():
        hours[m]=0
    hours[21] = 0.6
    hours[22]=0.4
    subst={
        "monthly_profile":months,
        "weekday_profile":weekdays,
        "daily_profile":hours
    }
    print(periods)
    success, returned_data, status_code, error_msg=BilateralApi.calculate_capacity_price(api_conn,periods, subst, 1000, 2000)
    print(returned_data)



def generate_sell_prices(api_conn):
    mw=500
    expiry = (datetime.today() + timedelta(days=10)).strftime("%Y-%m-%d")
    df = LemsApi.get_traded_products_df(api_conn)
    for index,row in df.iterrows():

        periods = [[row['ticker'],row['delivery_from'], row['delivery_until']]]

        success, res, status_code, error_msg = BilateralApi.calculate_contract_price(api_conn, periods, row['area'],
                                                                                     "NOK",
                                                                                     FwdCurveTypesEnum.PRICEIT.value)
        for result in res['period_prices']:
            print(result['period_tag'], result['contract_price'])
            LemsApi.add_order(api_conn, result['period_tag'], result['contract_price'], "NOK", mw, "SELL", "NORMAL", expiry)

def fetch_pricing_configurations(api_conn):
    json_pricing_configurations = BilateralApi.get_pricing_configurations(api_conn)
    print(json_pricing_configurations)

def fetch_pricing_configuration_pk(api_conn):
    pk = 2
    json_pricing_configurations = BilateralApi.get_pricing_configuration_by_pk(api_conn, pk)
    print(json_pricing_configurations)

def register_pricing_configuration(api_conn):
    pricing_configuration = PricingConfiguration()
    pricing_configuration.pk = 0
    pricing_configuration.currency_code = "EUR"
    pricing_configuration.wacc = 1
    pricing_configuration.inflation = 2
    pricing_configuration.price_areas = "NO1"
    pricing_configuration.basic_curve_model = "PRICEIT"
    pricing_configuration.yearly_epad_converging = 3
    pricing_configuration.spread_adjustment_epad = 4
    pricing_configuration.spread_adjustment_sys = 5
    pricing_configuration.counterpart_override = "http://127.0.0.1:8001/api/customers/companies/721/"
    pricing_configuration.is_default_config = True
    print(pricing_configuration.get_dict())
    BilateralApi.upsert_pricing_configuration(api_conn, pricing_configuration)

def generate_adjusted_curve(api_conn):
    success, returned_data, status_code, error_msg=BilateralApi.generate_adjusted_curve_from_config(api_conn,1)
    df_curve = pd.DataFrame(data=eval(returned_data))
    print(df_curve)

if __name__ == '__main__':
    #pd.set_option('display.max_rows', None)
    api_conn=init_api()

    #generate_sell_prices(api_conn)
    #fetch_pricing_configurations(api_conn)
    #register_test_capacity_requests(api_conn)
    test_capacity_config(api_conn)

    #register_pricing_configuration(api_conn)
    #get_deliveries(api_conn)
