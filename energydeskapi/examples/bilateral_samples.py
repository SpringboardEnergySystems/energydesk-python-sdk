import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.bilateral.bilateral_api import BilateralApi, PricingConfiguration
from energydeskapi.lems.lems_api import LemsApi
from datetime import datetime, timedelta
from energydeskapi.types.common_enum_types import PeriodResolutionEnum
from energydeskapi.types.common_enum_types import get_month_list,get_weekdays_list
from energydeskapi.types.fwdcurve_enum_types import FwdCurveModels
from energydeskapi.sdk.pandas_utils import get_summer_profile, get_winter_profile, get_workweek, get_weekend
import pandas as pd
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


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
    #df2=df.pivot_table(index='period_from', columns='counterpart', values='netpos', aggfunc='sum')
    #print(df2)
    #df = df.pivot(index='period_from', columns='counterpart', values='netpos')
    #print(df)

def calculate_price(api_conn):
    fromd="2023-10-01"
    untild = "2024-10-01"
    periods=[["A", fromd, untild]]

    fromd="2023-10-01"
    untild = "2026-10-01"
    periods.append(["B", fromd, untild])
    print(periods)
    df_curve, cprices, cpricedet=BilateralApi.calculate_contract_price_df(api_conn,periods, "NO1", "NOK",
                                            "PRICEIT",curve_resolution=PeriodResolutionEnum.DAILY.value,
                                         wacc=0.06, inflation=0,
                                        profile_type="BASELOAD",
                                        monthly_profile=get_winter_profile(),
                                        weekday_profile=get_workweek(),
                                        hours=list(range(5)))



def generate_sell_prices(api_conn):
    mw=500
    expiry = (datetime.today() + timedelta(days=10)).strftime("%Y-%m-%d")
    df = LemsApi.get_traded_products_df(api_conn)
    for index,row in df.iterrows():

        periods = [[row['ticker'],row['delivery_from'], row['delivery_until']]]

        success, res, status_code, error_msg = BilateralApi.calculate_contract_price(api_conn, periods, row['area'],
                                                                                     "NOK",
                                                                                     FwdCurveModels.PRICEIT.value)
        for result in res['period_prices']:
            print(result['period_tag'], result['contract_price'])
            LemsApi.add_order(api_conn, result['period_tag'], result['contract_price'], "NOK", mw, "SELL", "NORMAL", expiry)


def register_pricing_configuration(api_conn):
    pricing_configuration = PricingConfiguration()
    pricing_configuration.pk = 0
    pricing_configuration.currency_code = "EUR",
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


if __name__ == '__main__':
    api_conn=init_api()

    generate_sell_prices(api_conn)
    register_pricing_configuration(api_conn)
    #get_deliveries(api_conn)
