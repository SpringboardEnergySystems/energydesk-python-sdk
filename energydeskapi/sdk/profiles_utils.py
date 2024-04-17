import pandas as pd
from energydeskapi.types.common_enum_types import get_month_list,get_weekdays_list
import numpy as np
from datetime import date
from dateutil.relativedelta import relativedelta
import pytz
from energydeskapi.sdk.pandas_utils import make_empty_timeseries_df
def check_flat_profile(vmap):
    df=pd.DataFrame.from_dict(vmap, orient='index')
    print(df)
    df.rename(columns={0:'counts'}, inplace=True)
    return len(np.unique(df.counts)) == 1

def is_baseload(profile):
    b1 = check_flat_profile(profile['monthly_profile'])
    b2 = check_flat_profile(profile['weekday_profile'])
    b3 = check_flat_profile(profile['daily_profile'])
    return b1 and b2 and b3

def get_baseload_weekdays(entry_value=1.0):
    week=get_weekdays_list()
    return {k: entry_value for k in week}

def get_baseload_dailyhours(entry_value=1.0):
    hours=list(range(24))
    return {k: entry_value for k in hours}

# This function may be misguiding for users since identical months weights is not
# the same as basloed on a fixed volume.   Specify BASELOAD as profile category in addition
def get_baseload_months(entry_value=1.0):
    months=get_month_list()
    return {k: entry_value for k in months}

def get_flat_months(entry_value=1.0):
    months=get_month_list()
    return {k: entry_value for k in months}


# Used to get a default profile that factorize months based on hours. Using 2022 as sample year
def get_month_hours(month_idx):
    dt1=date(2022, month_idx,1)
    dt2 = dt1+ relativedelta(months=1)
    hours=(dt2-dt1).total_seconds() // 3600
    return hours


def get_default_profile_months():
    months=get_month_list()
    return {k: get_month_hours((idx+1)) for k,idx in zip(months, list(range(12)))}

def get_baseload_profile():
    return {
        'monthly_profile': get_baseload_months(),
        'weekday_profile': get_baseload_weekdays(),
        'daily_profile': get_baseload_dailyhours()
    }

def get_zero_profile():
    return {
        'monthly_profile': get_baseload_months(0.0),
        'weekday_profile': get_baseload_weekdays(0.0),
        'daily_profile': get_baseload_dailyhours(0.0)
    }
def normalize_elements(elements):
    sum=0
    for key in elements.keys():
        sum+=elements[key]
    if sum>0:
        for key in elements.keys():
            elements[key]=elements[key]/sum
    return elements

def generate_normalized_profile(profile):
    if not profile or profile is None:
        return get_baseload_profile()
    profile['monthly_profile'] = normalize_elements(profile['monthly_profile']) #if 'monthly_profile' in profile['monthly_profile'] else profile['monthly_profile']
    profile['weekday_profile'] = normalize_elements(profile['weekday_profile'])
    profile['daily_profile'] = normalize_elements(profile['daily_profile'])
    return profile


def __stringify_dictionary(d):
    newdict={}
    for key in d.keys():
        newdict[str(key)]=d[key]
    return newdict
def __convert_from_named_profiles(profile):
    months=profile['monthly_profile']

    monthkeys={(index+1): months[month] for index, month in enumerate(get_month_list()) if month}
    profile['monthly_profile']=monthkeys
    weekdays=profile['weekday_profile']
    weekdayskeys={(index): weekdays[month] for index, month in enumerate(get_weekdays_list()) if month}
    profile['weekday_profile']=weekdayskeys
    dayshours=profile['daily_profile']
    dayshours=__stringify_dictionary(dayshours)  # Otherwise the lookup below fails
    hourlykeys={(index): dayshours[str(index)] for index in list(range(24))}
    profile['daily_profile']=hourlykeys
    return profile


def relative_profile_to_dataframe(period_from, period_until,relative_profile, active_tz=pytz.timezone("Europe/Oslo")):

    try:
        calender_profile=__convert_from_named_profiles(relative_profile)
    except Exception as e:
        #traceback.print_exc()
        calender_profile=relative_profile

    monthly_weights=calender_profile['monthly_profile']
    weekly_weights = calender_profile['weekday_profile']
    daily_weights = calender_profile['daily_profile']

    df=make_empty_timeseries_df(period_from, period_until, "H", active_tz)


    df['timestamp'] = df.index


    df['monthly_weight'] = df.apply(lambda x: monthly_weights[x['timestamp'].month], axis=1)
    df['weekday_weight'] = df.apply(lambda x: weekly_weights[x['timestamp'].dayofweek], axis=1)
    df['hour_weight'] = df.apply(lambda x: daily_weights[x['timestamp'].hour], axis=1)
    df['hourly_weight'] =df['monthly_weight']*df['weekday_weight']*df['hour_weight']

    return df[['timestamp','hourly_weight']]


if __name__ == '__main__':
    months=get_baseload_months()
    weekdays=get_baseload_weekdays()
    hours=get_baseload_dailyhours()
    print(months)
    print(weekdays)
    print(hours)
