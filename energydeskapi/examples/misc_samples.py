import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.system.system_api import SystemApi
from energydeskapi.types.company_enum_types import UserRoleEnum
from energydeskapi.sdk.datetime_utils import prev_weekday
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytz
from energydeskapi.sdk.pandas_utils import make_empty_timeseries_df
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])

def test_pandas_year(api_conn):
    active_tz = pytz.timezone("Europe/Oslo")
    t1="2023-10-31 23:00:00+00:00"
    t2="2026-10-31 23:00:00+00:00"
    df=make_empty_timeseries_df(t1, t2, "YS", active_tz, predefined_columns=['ticker'])
    print(df)
def test_pandas(api_conn):
    active_tz = pytz.timezone("Europe/Oslo")
    t2="2023-12-31 23:00:00+00:00"
    t1="2023-07-31 22:00:00+00:00"

    df=make_empty_timeseries_df(t1, t2, "H", active_tz, predefined_columns=['ticker'])
    print(df)
    df=make_empty_timeseries_df(t1, t2, "MS", active_tz, predefined_columns=['ticker'])
    print(df)

    t1="2023-07-01 00:00:00+02:00"
    t2="2023-08-01 00:00:00+02:00"
    df=make_empty_timeseries_df(t1, t2, "H", active_tz, predefined_columns=['ticker'])
    print(df)
    df=make_empty_timeseries_df(t1, t2, "MS", active_tz, predefined_columns=['ticker'])
    print(df)

    df=make_empty_timeseries_df(t1, t2, None, active_tz, predefined_columns=['ticker'])
    print(df)

def small_sample():

    t1="2023-07-01 00:00:00+02:00"
    t2="2024-08-01 00:00:00+02:00"
    df=make_empty_timeseries_df(t1, t2, "MS", "Europe/Oslo", predefined_columns=['period_from', 'period_until'])
    df['period_from']=df.index
    df['hours']=0
    def calc_end_date(row):
        row['period_until']= row['period_from'] + relativedelta(months=1)
        seconds=(row['period_until']-row['period_from']).total_seconds()
        row['hours']=seconds // 3600
        return row
    df=df.apply(calc_end_date, axis=1)
    print(df)


if __name__ == '__main__':
    api_conn = init_api()

    small_sample()
    #get_sysmanager_info(api_conn)
