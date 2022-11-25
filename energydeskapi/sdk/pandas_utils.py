
import pandas as pd
import numpy as np
import calendar
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def make_none_tz( utc_dt):
    tmp =str(utc_dt)[:19]
    return datetime.strptime(tmp, '%Y-%m-%d %H:%M:%S')

def make_empty_timeseries_df(period_from, period_to, pandas_res):
    df=pd.DataFrame()
    ix = pd.date_range(start=make_none_tz(period_from), end=make_none_tz(period_to), freq=pandas_res)
    df_new = df.reindex(ix, fill_value='NaN')
    return df_new

def check_pattern(row):
    pass
def create_yearly_pattern(hourly=True):
    data = np.random.rand(366)
    dt1=datetime.today().replace(month=1, day=1, second=0, microsecond=0, hour=0, minute=0)
    df=make_empty_timeseries_df(dt1,
                                dt1 + relativedelta(years=1),
                                "H")
    df['pattern']=0


if __name__ == '__main__':
    create_yearly_pattern()