import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.bilateral.bilateral_api import BilateralApi
from energydeskapi.lems.lems_api import LemsApi
from datetime import datetime, timedelta
from energydeskapi.types.common_enum_types import PeriodResolutionEnum
from energydeskapi.types.common_enum_types import get_month_list,get_weekdays_list
from energydeskapi.types.fwdcurve_enum_types import FwdCurveInternalEnum
from energydeskapi.sdk.pandas_utils import get_summer_profile, get_winter_profile, get_workweek, get_weekend
import pandas as pd
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def calculate_price(api_conn):
    fromd="2023-10-01"
    untild = "2024-10-01"
    periods=[["A", fromd, untild]]

    fromd="2023-10-01"
    untild = "2026-10-01"
    periods.append(["B", fromd, untild])
    print(periods)
    success, res, status_code, error_msg =BilateralApi.calculate_contract_price(api_conn,periods, "NO1", "NOK",
                                            "PRICEIT",
                                        contract_type="PROFILE",
                                        monthly_profile=get_month_list(),
                                        weekday_profile=get_workweek())

    period_prices = res['period_prices']
    for p in period_prices:
        contract_price = p['contract_price']
        print("Contract price", contract_price)

    # df_curve = pd.DataFrame(data=eval(res['forward_curve']))
    #
    # period_prices=res['period_prices']
    # for p in period_prices:
    #     df_pricing = pd.DataFrame(data=eval(p['pricing_details']))
    #     contract_price=p['contract_price']
    #     print(df_pricing)
    #     print("Contract price", contract_price)

def generate_sell_prices(api_conn):
    mw=500
    expiry = (datetime.today() + timedelta(days=10)).strftime("%Y-%m-%d")
    df = LemsApi.get_traded_products(api_conn)
    for index,row in df.iterrows():
        print("Calculating fixed price for ", row['ticker'])
        periods = [[row['ticker'],row['delivery_from'], row['delivery_until']]]
        LemsApi.add_order(api_conn, row['ticker'], 1100, "NOK", mw, "SELL", "NORMAL", expiry)
        continue
        success, res, status_code, error_msg = BilateralApi.calculate_contract_price(api_conn, periods, mw, row['area'],
                                                                                     "NOK",
                                                                                     FwdCurveInternalEnum.CUBIC_SPLINE.value)
        for result in res['period_prices']:
            print(result['period_tag'], result['contract_price'])
            LemsApi.add_order(api_conn, result['period_tag'], result['contract_price'], "NOK", mw, "SELL", "NORMAL", expiry)


if __name__ == '__main__':
    api_conn=init_api()
    #print(PeriodResolutionEnum._value2member_map_['Daily'])
    calculate_price(api_conn)
