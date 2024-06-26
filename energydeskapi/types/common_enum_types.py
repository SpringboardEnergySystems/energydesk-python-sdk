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
    if resolution_enum==PeriodResolutionEnum.HOURLY:
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
    if resolution_enum==PeriodResolutionEnum.HOURLY:
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

# Server gets Monthly, Hourly etc as input, and needs this conversion
def resolution_str_to_pandas_freq(resolution_str):
    return resolution_to_pandas_freq(PeriodResolutionEnum(resolution_str))


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