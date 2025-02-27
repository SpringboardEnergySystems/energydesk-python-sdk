from enum import Enum
from dateutil.relativedelta import relativedelta

from datetime import datetime, timedelta
import calendar as cal

def get_weekdays_list(start=0):
    #start = 0#[d for d in cal.day_name].index(weekday)
    return [cal.day_name[(i+start) % 7] for i in range(7)]
def get_month_list():
    start = datetime(2022,1,1)
    return [(start + relativedelta(months=i)).strftime('%B') for i in range(12)]

class CountryPrefEnum(Enum):
    NORWAY = 1
    SWEDEN = 2
    UK = 3
    US = 4
    GERMANY=5


class PeriodResolutionEnum(Enum):
    MINUTES = "1min"
    FIVEMIN= "5min"
    FIFTEENMIN = "15min"
    HOURLY = "Hourly"
    DAILY = "Daily"
    WEEKLY = "Weekly"
    SEMI_MONTHLY = "SemiMonthly"
    MONTHLY = "Monthly"
    QUARTERLY = "Quarterly"
    YEARLY = "Yearly"


# Numeric to represent resolution
def period_resolution_key(instance):
    return list(PeriodResolutionEnum).index(instance) + 1

PERIOD_CHOICES=[el.value for el in PeriodResolutionEnum]

def period_addition_relativedelta(resolution_enum):
    if resolution_enum==PeriodResolutionEnum.MINUTES:
        return relativedelta(minutes=1)
    elif resolution_enum==PeriodResolutionEnum.FIVEMIN:
        return relativedelta(minutes=5)
    elif resolution_enum==PeriodResolutionEnum.FIFTEENMIN:
        return relativedelta(minutes=15)
    elif resolution_enum==PeriodResolutionEnum.HOURLY:
        return relativedelta(hours=1)
    elif resolution_enum==PeriodResolutionEnum.DAILY:
        return relativedelta(days=1)
    elif resolution_enum==PeriodResolutionEnum.WEEKLY:
        return relativedelta(weeks=1)
    elif resolution_enum==PeriodResolutionEnum.MONTHLY:
        return relativedelta(months=1)
    elif resolution_enum==PeriodResolutionEnum.SEMI_MONTHLY:
        return relativedelta(weeks=2)
    elif resolution_enum==PeriodResolutionEnum.QUARTERLY:
        return relativedelta(months=3)
    elif resolution_enum==PeriodResolutionEnum.YEARLY:
        return relativedelta(years=1)
    return relativedelta(days=0)  #Default

def resolution_to_pandas_freq(resolution_enum):
    if resolution_enum==PeriodResolutionEnum.MINUTES:
        return "1min"
    elif resolution_enum==PeriodResolutionEnum.FIVEMIN:
        return "5min"
    elif resolution_enum==PeriodResolutionEnum.FIFTEENMIN:
        return "15min"
    elif resolution_enum==PeriodResolutionEnum.HOURLY:
        return "H"
    elif resolution_enum==PeriodResolutionEnum.DAILY:
        return "D"
    elif resolution_enum==PeriodResolutionEnum.WEEKLY:
        return "W"
    elif resolution_enum==PeriodResolutionEnum.SEMI_MONTHLY:
        return "SMS"
    elif resolution_enum==PeriodResolutionEnum.MONTHLY:
        return "MS"
    elif resolution_enum==PeriodResolutionEnum.QUARTERLY:
        return "QS"
    elif resolution_enum==PeriodResolutionEnum.YEARLY:
        return "YS"
    return "D"  #Default

# This is not accurate for months and higher
def period_resolution_hours(resolution_enum):
    if resolution_enum==PeriodResolutionEnum.MINUTES:
        return 1/60
    elif resolution_enum==PeriodResolutionEnum.FIVEMIN:
        return 5/60
    elif resolution_enum==PeriodResolutionEnum.FIFTEENMIN:
        return 15/60
    elif resolution_enum==PeriodResolutionEnum.HOURLY:
        return 1
    elif resolution_enum==PeriodResolutionEnum.DAILY:
        return 24
    elif resolution_enum==PeriodResolutionEnum.WEEKLY:
        return 7*24
    elif resolution_enum==PeriodResolutionEnum.MONTHLY:
        return 30*24
    elif resolution_enum==PeriodResolutionEnum.SEMI_MONTHLY:
        return 60*24
    elif resolution_enum==PeriodResolutionEnum.QUARTERLY:
        return 90*24
    elif resolution_enum==PeriodResolutionEnum.YEARLY:
        return 365*24
    return 1

# Server gets Monthly, Hourly etc as input, and needs this conversion
def resolution_str_to_pandas_freq(resolution_str):
    return resolution_to_pandas_freq(PeriodResolutionEnum(resolution_str))

# Server gets Monthly, Hourly etc as input, and needs this conversion
def resolution_str_to_period_hours(resolution_str):
    return period_resolution_hours(PeriodResolutionEnum(resolution_str))

"""
PANDAS FREQUENCIES

Alias    Description
B        business day frequency
C        custom business day frequency
D        calendar day frequency
W        weekly frequency
M        month end frequency
SM       semi-month end frequency (15th and end of month)
BM       business month end frequency
CBM      custom business month end frequency
MS       month start frequency
SMS      semi-month start frequency (1st and 15th)
BMS      business month start frequency
CBMS     custom business month start frequency
Q        quarter end frequency
BQ       business quarter end frequency
QS       quarter start frequency
BQS      business quarter start frequency
A, Y     year end frequency
BA, BY   business year end frequency
AS, YS   year start frequency
BAS, BYS business year start frequency
BH       business hour frequency
H        hourly frequency
T, min   minutely frequency
S        secondly frequency
L, ms    milliseconds
U, us    microseconds
N        nanoseconds
"""