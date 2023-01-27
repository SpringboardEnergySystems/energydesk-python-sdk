import pandas as pd
import numpy as np
import calendar
import calendar
from datetime import datetime, timedelta
from pandas.errors import ParserError
import pytz
from dateutil.relativedelta import relativedelta
from energydeskapi.types.common_enum_types import get_month_list,get_weekdays_list


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

if __name__ == '__main__':
    months=get_baseload_months()
    weekdays=get_baseload_weekdays()
    hours=get_baseload_dailyhours()
    print(months)
    print(weekdays)
    print(hours)