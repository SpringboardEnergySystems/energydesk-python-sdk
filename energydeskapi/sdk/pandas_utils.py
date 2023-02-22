
import pandas as pd
import numpy as np
import calendar
import calendar
from datetime import datetime, timedelta
from pandas.errors import ParserError
import pytz
from dateutil.relativedelta import relativedelta
from energydeskapi.types.common_enum_types import get_month_list,get_weekdays_list
def make_none_tz( utc_dt):
    tmp =str(utc_dt)[:19]
    return datetime.strptime(tmp, '%Y-%m-%d %H:%M:%S')

def make_empty_timeseries_df(period_from, period_to, pandas_res, timezone=None):
    df=pd.DataFrame()
    ix = pd.date_range(start=make_none_tz(period_from), end=make_none_tz(period_to), freq=pandas_res)
    df_new = df.reindex(ix, fill_value='NaN')
    df_new=df_new.tz_localize(pytz.UTC)
    df_new = df_new.tz_convert(timezone)
    return df_new

def apply_calendar_pattern_old(df, months, weekdays, hours = range(24)):
    def check_pattern(row):
        v= 1 if row.name.strftime('%B') in months \
            and calendar.day_name[row.name.weekday()]  in weekdays \
            and row.name.hour in hours else 0
        return v
    df['profile']=df.apply(check_pattern, axis=1)
    return df

def apply_calendar_pattern(df, months, weekdays, hours=list(range(24))):
    def check_tuples(lst):
        if len(lst)==0:
            return False
        return type(lst[0])==tuple
    # If ínputs are plain lists, create binary maps with 1.0 as factors
    if type(months)==dict:
        month_map=months
    else:
        month_map = {k[0]: k[1] for k in months} if check_tuples(months) else {k: 1.0 for k in months}
    if type(weekdays)==dict:
        weekday_map=weekdays
    else:
        weekday_map = {k[0]: k[1] for k in weekdays} if check_tuples(weekdays) else {k: 1.0 for k in weekdays}

    if type(hours)==dict:
        hourly_map={int(k): hours[k] for k in hours.keys()}
    else:
        hourly_map = {int(k[0]): k[1] for k in hours} if check_tuples(hours) else {k: 1.0 for k in hours}

    def check_pattern(row):
        mname=row.name.strftime('%B')
        wdname=calendar.day_name[row.name.weekday()]
        mnth_factor = month_map[mname] if mname in month_map else 0
        wday_factor = weekday_map[wdname] if wdname in weekday_map else 0
        hour_factor=hourly_map[row.name.hour] if row.name.hour in hourly_map else 0
        v = mnth_factor*wday_factor*hour_factor
        #v = min([mnth_factor, wday_factor, hour_factor])
        return v
    df['profile'] = df.apply(check_pattern, axis=1)
    return df

def create_empty_df_with_pattern( months, weekdays):
    dt1=datetime.today().replace(month=1, day=1, second=0, microsecond=0, hour=0, minute=0)
    df=make_empty_timeseries_df(dt1,
                                dt1 + relativedelta(years=1),
                                "H")

    df['timestamp']=df.index
    return apply_calendar_pattern(df, months, weekdays)


def convert_dataframe_to_localtime(df):
    norzone = pytz.timezone('Europe/Oslo')
    for c in df.columns[df.dtypes == 'object']:  # don't cnvt num
        try:
            df[c] = pd.to_datetime(df[c])
            df[c] = df[c].dt.tz_convert(tz=norzone)
        except (ParserError, ValueError):  # Can't cnvrt some
            pass  # ...so leave whole column as-is unconverted
    df.index = pd.to_datetime(df.index)
    df.index = df.index.tz_convert(tz=norzone)
    return df



def get_workweek():
    week=get_weekdays_list()[0:5]
    return week
def get_weekend():
    week=get_weekdays_list()[5:7]
    return week
def get_winter_profile():
    m1=get_month_list()[0:4]
    m1.extend(get_month_list()[8:])
    return m1
def get_summer_profile():
    m1=get_month_list()[4:8]
    return m1

if __name__ == '__main__':
    tz = pytz.timezone("Europe/Oslo")
    year_start = datetime.today().replace(month=3, day=1, hour=0, minute=0, second=0, microsecond=0)
    tz_aware_start = tz.localize(year_start)
    tz_aware_start=tz_aware_start.astimezone(pytz.utc)
    year_end=tz_aware_start + relativedelta(years=3)
    df=make_empty_timeseries_df(tz_aware_start, year_end, "H", tz )
    df['one']=1
    print(df['2023-10-29':'2023-10-30'])