import pandas as pd
from energydeskapi.types.common_enum_types import get_month_list,get_weekdays_list
import numpy as np
from datetime import date
from dateutil.relativedelta import relativedelta
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

def get_baseload_weekdays():
    week=get_weekdays_list()
    return {k: 1.0 for k in week}

def get_baseload_dailyhours():
    hours=list(range(24))
    return {k: 1.0 for k in hours}

# This function may be misguiding for users since identical months weights is not
# the same as basloed on a fixed volume.   Specify BASELOAD as profile category in addition
def get_baseload_months():
    months=get_month_list()
    return {k: 1.0 for k in months}

def get_flat_months():
    months=get_month_list()
    return {k: 1.0 for k in months}


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

if __name__ == '__main__':
    months=get_baseload_months()
    weekdays=get_baseload_weekdays()
    hours=get_baseload_dailyhours()
    print(months)
    print(weekdays)
    print(hours)
