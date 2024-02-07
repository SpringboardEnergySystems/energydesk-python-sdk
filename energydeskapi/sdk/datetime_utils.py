import pytz
from dateutil import parser
from datetime import date, datetime, timedelta
import pendulum
from pandas import Timestamp
# WIll convert both naive and datetimes that were previously localized
def localize_datetime_safe(dt, tz=pytz.timezone("UTC")):
    try:
        loc_dt=tz.localize(dt)
    except:
        loc_dt=dt.astimezone(tz)
    return loc_dt

def localize_datetime(dt,  loczone="UTC"):
    timezone = pytz.timezone(loczone)
    try:
        d_aware = timezone.localize(dt)
    except:
        return convert_timezone(dt, loczone)
    return d_aware

def convert_timezone(dt,  loczone="UTC"):
    timezone = pytz.timezone(loczone)
    converted = dt.astimezone(timezone)
    return converted

def localize_strtime(strtime, loczone="Europe/Oslo"):
    unaware_dt = parser.isoparse(strtime) if type(strtime)==str else strtime
    return localize_datetime(unaware_dt, loczone)



def tz_aware(dt):
    return dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None

def convert_loc_datetime_to_utcstr(naive_local_dt, loczone="Europe/Oslo"):
    local_tz = pytz.timezone(loczone)
    if not tz_aware(naive_local_dt):
        d_aware = local_tz.localize(naive_local_dt)
    else:
        d_aware=naive_local_dt  # It was tz aware
    d_utc = d_aware.astimezone(pytz.UTC)
    s_dt_utc = d_utc.strftime('%Y-%m-%dT%H:%M:%S+00:00')
    return s_dt_utc




def convert_tzaware_datetime_to_utcstr(tzaware_local_dt):
    d_utc = tzaware_local_dt.astimezone(pytz.UTC)
    s_dt_utc = d_utc.strftime('%Y-%m-%dT%H:%M:%S+00:00')
    return s_dt_utc

def convert_datime_to_locstr(dt, loczone="Europe/Oslo"):
    tz=pytz.timezone(loczone)
    dtutc=localize_datetime_safe(dt, tz)
    s_dt = dtutc.strftime('%Y-%m-%dT%H:%M:%S%z')
    timestamp_string = "{0}:{1}".format(
        s_dt[:-2],
        s_dt[-2:]
    )
    return timestamp_string

def localized_datetimestr_from_datetime(datetime_val, loczone="Europe/Oslo"):
    """ Converts datetime from UTC
    """
    print("Asked to convert", datetime_val)
    if type(datetime_val) == str:
        d_loc=pendulum.parse(datetime_val)#, loczone).to_datetime_string()

    else:
        d_loc=pendulum.from_timestamp(datetime_val)
    print(d_loc)
    d_loc=d_loc.in_tz(loczone)
    print(d_loc)
    return str(d_loc)

# Make sure we are in normal time when getting date part
# I.e. 2024-12-31T23:00:00+00:00  becomes 2025-01-01 in Europe/Oslo
def localized_datestr_from_datetime(datetime_val, loczone="Europe/Oslo"):
    tmp=localized_datetimestr_from_datetime(datetime_val, loczone)
    return tmp[:10]


def add_business_days(pendulum_start_date, day_count):
    business_days_to_add = day_count
    current_date = pendulum_start_date
    while business_days_to_add > 0:
        current_date = current_date.add(days=1)
        weekday = current_date.weekday()
        if weekday >= 5: # sunday = 6
            continue
        business_days_to_add -= 1
    return current_date

# Data retrieved from server are in UTC time ("GMT without daylight savings time")
# This function converts to local time
def convert_datetime_from_utc(utc_str, loczone="Europe/Oslo"):
    """ Converts datetime from UTC
    """
    timezone = pytz.timezone(loczone)
    utc_dt=parser.isoparse(str(utc_str))
    d_loc = utc_dt.astimezone(timezone)
    return d_loc

def conv_from_pendulum(pendulum_dt, tz="UTC"):
    if type(pendulum_dt)== datetime or type(pendulum_dt)==Timestamp:
        return pendulum_dt
    timezone = pytz.timezone(tz) if type(tz)==str else tz
    parsed_dt= datetime.fromisoformat(str(pendulum_dt))
    if tz_aware(parsed_dt):
        return parsed_dt
    return parsed_dt.astimezone(timezone)

def safe_set_utc(indate):
    try:
        outdate=indate.astimezone(pytz.utc)
    except:
        outdate = indate
    return outdate

def calc_seconds(date1, date2):
    duration=date2-date1
    return float(duration.total_seconds())

def overlapping_seconds(calc_period_from, calc_period_until, test_period_from, test_period_until):
    period_from=safe_set_utc(test_period_from)
    period_until = safe_set_utc(test_period_until)
    calc_period_from=safe_set_utc(calc_period_from)
    calc_period_until = safe_set_utc(calc_period_until)
    if calc_period_until<period_from:
        return 0
    if calc_period_from>=period_until:
        return 0
    if calc_period_from<=period_from and calc_period_until>=period_until:
        return calc_seconds(period_from, period_until)
    if calc_period_from>=period_from and calc_period_until<=period_until:
        return calc_seconds(calc_period_from, calc_period_until)
    if calc_period_from>period_from:
        return calc_seconds(calc_period_from, period_until)
    if calc_period_until<period_until:
        return calc_seconds(period_from, calc_period_until)
    return 0


def prev_weekday(d, weekday):
    days = d.isoweekday() - weekday -1
    if days < 0:
        days += 7
    previous_date = d - timedelta(days=days)
    previous_date=localize_datetime(previous_date, "Europe/Oslo")
    return previous_date#date(previous_date.year, previous_date.month, previous_date.day)

def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days_ahead)
