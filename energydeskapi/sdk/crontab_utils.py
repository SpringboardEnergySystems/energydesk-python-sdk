from energydeskapi.sdk.pandas_utils import make_empty_timeseries_df
from croniter import croniter
import pytz
from datetime import datetime
from energydeskapi.sdk.datetime_utils import conv_from_pendulum
import pandas as pd
def generate_dataframe(period_from, period_until, crontab):
    df2 = make_empty_timeseries_df(period_from, period_until, "H", timezone=pytz.timezone("Europe/Oslo"),
                                   predefined_columns=['standby'])

    df2['standby'] = False
    df2 = df2.tz_convert("Europe/Oslo")
    base=conv_from_pendulum(period_from, "Europe/Oslo")
    end = conv_from_pendulum(period_until, "Europe/Oslo")
    iter = croniter(crontab, base)
    n = None#iter.get_next(datetime)
    #records = []
    print(df2)
    while n is None or n < end:
        n = iter.get_next(datetime)
        if n >= base and n < end:
            mask = ((df2.index == n) )
            df2.loc[mask, 'standby']=True
    df2['hour']=df2.index
    return df2
