import pandas as pd
from energydeskapi.types.common_enum_types import get_month_list,get_weekdays_list
import numpy as np
def check_flat_profile(vmap):
    df=pd.DataFrame.from_dict(vmap, orient='index')
    df.rename(columns={0:'counts'}, inplace=True)
    return len(np.unique(df.counts)) == 1

def is_baseload(profile):
    b1=check_flat_profile(profile['monthly_profile'])
    b2 = check_flat_profile(profile['weekday_profile'])
    b3 = check_flat_profile(profile['daily_profile'])
    return b1 and b2 and b3

def get_baseload_weekdays():
    week=get_weekdays_list()
    return {k: 1.0 for k in week}

def get_baseload_dailyhours():
    hours=list(range(24))
    return {k: 1.0 for k in hours}

def get_baseload_months():
    months=get_month_list()
    return {k: 1.0 for k in months}

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
    profile['monthly_profile'] = normalize_elements(profile['monthly_profile'])
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
