
import pandas as pd
import numpy as np
import calendar
import calendar
from datetime import datetime, timedelta
from pandas.errors import ParserError
import pytz
from dateutil.relativedelta import relativedelta
from energydeskapi.types.common_enum_types import get_month_list,get_weekdays_list
from decimal import Decimal
import pendulum
from energydeskapi.sdk.datetime_utils import conv_from_pendulum
def make_none_tz( utc_dt):
    tmp =str(utc_dt)[:19]
    return datetime.strptime(tmp, '%Y-%m-%d %H:%M:%S')

def check_convert_datetime(d, timezone=None):
    if d.tzinfo is not None and d.tzinfo.utcoffset(d) is not None:
        d = d.astimezone(pytz.UTC)
        return d
    else:
        if timezone is None:
            timezone=pytz.UTC
        d = timezone.localize(d)
        d = d.astimezone(pytz.UTC)
        return d

def make_empty_timeseries_df_new(period_from, period_to, pandas_res, timezone=pytz('UTC'), predefined_columns=[]):
    period_from = pendulum.parse(str(period_from))
    period_to = pendulum.parse(str(period_to))

    generation_timezone = timezone if pandas_res != "H" else pytz('UTC')
    period_from = period_from.in_tz(generation_timezone)
    period_to = period_to.in_tz(generation_timezone)

    # Function to convert pendulum to datetime, assuming it's defined elsewhere
    def conv_from_pendulum(pendulum_datetime, tz=None):
        return pendulum_datetime.to_datetime_string()

    dtfrom = conv_from_pendulum(period_from, tz=generation_timezone)
    dtuntil = conv_from_pendulum(period_to, tz=generation_timezone)
    dtfrom = pd.to_datetime(dtfrom).replace(tzinfo=None)
    dtuntil = pd.to_datetime(dtuntil).replace(tzinfo=None)

    # Adjust period_to for monthly resolution to ensure at least one row is returned
    if pandas_res == "M" and period_from.format("YYYY-MM") == period_to.format("YYYY-MM"):
        period_to = period_to.add(months=1)
        dtuntil = conv_from_pendulum(period_to, tz=generation_timezone)
        dtuntil = pd.to_datetime(dtuntil).replace(tzinfo=None)

    # Adjustment for "YS" to include the entire year
    if pandas_res == "YS":
        dtfrom = dtfrom.replace(month=1, day=1)
        dtuntil = dtuntil.replace(month=1, day=1) + relativedelta(years=1)

    if len(predefined_columns) == 0:
        df = pd.DataFrame()
    else:
        df = pd.DataFrame(columns=predefined_columns)

    ix = pd.date_range(start=dtfrom, end=dtuntil, freq=pandas_res)
    df_new = df.reindex(ix, fill_value='NaN')
    df_new = df_new.tz_localize(generation_timezone, ambiguous='infer')

    if pandas_res == "H":
        df_new = df_new.tz_convert(timezone)

    if pandas_res is None:
        return df_new.head(1)

    if len(df_new.index) > 1:
        df_new = df_new.head(-1)

    return df_new

def make_empty_timeseries_df(period_from, period_to, pandas_res, timezone=pytz.timezone("UTC"), predefined_columns=[]):
    period_from=pendulum.parse(str(period_from)) if period_from!= str else pendulum.parse(period_from)
    period_to =pendulum.parse(str(period_to)) if period_to!= str else  pendulum.parse(period_to)

    generation_timezone=timezone if pandas_res is not "H" else pytz.timezone("UTC")
    period_from=period_from.in_timezone(generation_timezone)
    period_to = period_to.in_timezone(generation_timezone)
    dtfrom=conv_from_pendulum(period_from, tz=generation_timezone)
    dtuntil = conv_from_pendulum(period_to, tz=generation_timezone)
    dtfrom = dtfrom.replace(tzinfo=None)
    dtuntil = dtuntil.replace(tzinfo=None)
    if pandas_res=="YS":
        dtfrom=dtfrom.replace(month=1)
        dtuntil=(dtuntil + relativedelta(years=1))#.replace(month=1)


    if len(predefined_columns)==0:
        df=pd.DataFrame()
    else:
        df = pd.DataFrame(columns=predefined_columns)
    if pandas_res is None:
        ix = pd.date_range(start=dtfrom, end=dtuntil)
    else:
        ix = pd.date_range(start=dtfrom, end=dtuntil, freq=pandas_res)

    df_new = df.reindex(ix, fill_value='NaN')
    df_new = df_new.tz_localize(generation_timezone)
    if pandas_res == "H":
        df_new = df_new.tz_convert(timezone)
    if pandas_res is None:  #No resolution, so only return first line defininig the full period
        return df_new.head(1)
    if len(df_new.index)>1:  #Will generate the last entry
        df_new=df_new.head(-1)
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

# Usage , with a dataframe full of decimals: df = df.apply(cast_decimals_to_number, axis=1)
def cast_decimals_to_number(row):
    for c in list(row.index):
        if type(row[c])==Decimal:
            row[c] = float(row[c])
    return row

if __name__ == '__main__':
    tz = pytz.timezone("Europe/Oslo")
    year_start = datetime.today().replace(month=2, day=1, hour=0, minute=0, second=0, microsecond=0)
    tz_aware_start = tz.localize(year_start)
    #tz_aware_start=tz_aware_start.astimezone(pytz.UTC)
    year_end=tz_aware_start + relativedelta(months=1)
    df=make_empty_timeseries_df(tz_aware_start, year_end, "H", tz )
    df['one']=1
    print(df)
