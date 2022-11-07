import logging
from energydeskapi.contracts.contracts_api import ContractsApi, Contract
from energydeskapi.gos.gos_api import GosApi, GoContract
from energydeskapi.sdk.common_utils import init_api
from moneyed import EUR
from energydeskapi.curves.curve_api import CurveApi
from energydeskapi.types.location_enum_types import LocationTypeEnum
from datetime import datetime, timedelta
from energydeskapi.sdk.datetime_utils import convert_datime_to_utcstr, convert_datime_to_locstr
from energydeskapi.types.contract_enum_types import ContractStatusEnum, ContractTypeEnum, GosEnergySources
from energydeskapi.types.market_enum_types import CommodityTypeEnum, InstrumentTypeEnum, MarketEnum
from energydeskapi.sdk.money_utils import FormattedMoney
from energydeskapi.types.fwdcurve_enum_types import FwdCurveInternalEnum
import json
import pandas as pd
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def generate_curve(api_conn):
    fromd="2022-10-01"
    untild = "2024-10-01"
    def process_dframe(df, name):

        df['date'] = pd.to_datetime(df['date'])
        df.index=df['date']
        df=df[['date', 'price']]
        df2 = df.resample('MS',  on='date').mean()
        df=df.drop(['date'], axis=1)
        return df.rename({'price': name}, axis=1),df2.rename({'price': name}, axis=1)


    success, df, status_code, error_msg =CurveApi.generate_forward_curve_df(api_conn,fromd, untild, "NO1", "NOK",
                                            FwdCurveInternalEnum.CUBIC_SPLINE.value)

    df.index=df.date
    print(df)
    df['index'] = pd.to_datetime(df.index)
    df['monthly'] = df.groupby(df['index'].dt.strftime('%Y%m')).price.transform('mean')
    print(df)
    # df = pd.DataFrame(data=eval(jsonres))
    # daily, monthly=process_dframe(df, "NO1")
    # jsonres=CurveApi.get_hourly_price_curve(api_conn, fromd, untild, "NO5", "NOK")
    # if jsonres is not None:
    #     df = pd.DataFrame(data=eval(jsonres))
    #     daily_sub, monthly_sub=process_dframe(df,"NO5")
    #     daily["NO5"]= daily_sub["NO5"]
    #     monthly["NO5"] = monthly_sub["NO5"]
    # print(daily, monthly)

if __name__ == '__main__':
    api_conn=init_api()
    generate_curve(api_conn)
