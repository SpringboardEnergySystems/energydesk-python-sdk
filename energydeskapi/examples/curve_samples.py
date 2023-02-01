import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.curves.curve_api import CurveApi
from energydeskapi.types.common_enum_types import PeriodResolutionEnum
from energydeskapi.types.fwdcurve_enum_types import FwdCurveInternalEnum
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


def retrieve_stored_curve(api_conn):
    for area in ['SYS', 'NO1','NO2','NO3','NO4','NO5']:
        for curr in ['NOK','EUR']:
            success, df, status_code, error_msg =CurveApi.retrieve_latest_forward_curve_df(api_conn ,
                                                   area,
                                        curr, "PRICEIT", PeriodResolutionEnum.HOURLY.value)
            if success:
                print(df)
                df.index = df.index.tz_localize(None)
                df = df.drop(columns=['period_from', 'period_until','date'])

                print(df)
                df.to_excel("priskurve_" + area + "_" + curr + ".xlsx")

if __name__ == '__main__':
    api_conn=init_api()
    retrieve_stored_curve(api_conn)
