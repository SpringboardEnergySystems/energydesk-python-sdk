import pytz
from dateutil import parser
from datetime import date, datetime, timedelta
import pendulum

# WIll convert both naive and datetimes that were previously localized
def localize_datetime_safe(dt, tz=pytz.timezone("UTC")):
    try:
        loc_dt=tz.localize(dt)
    except:
        loc_dt=dt.astimezone(tz)
    return loc_dt

def localize_datetime(dt,  loczone="UTC"):
    timezone = pytz.timezone(loczone)
    d_aware = timezone.localize(dt)
    return d_aware

def convert_timezone(dt,  loczone="UTC"):
    timezone = pytz.timezone(loczone)
    converted = dt.astimezone(timezone)
    return converted

def localize_strtime(strtime, loczone):
    unaware_dt = parser.isoparse(strtime)
    return localize_datetime(unaware_dt)

def convert_loc_datetime_to_utcstr(naive_local_dt, loczone="Europe/Oslo"):
    local_tz = pytz.timezone(loczone)
    d_aware = local_tz.localize(naive_local_dt)
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


# Data retrieved from server are in UTC time ("GMT without daylight savings time")
# This function converts to local time
def convert_datetime_from_utc(utc_str, loczone="Europe/Oslo"):
    """ Converts datetime from UTC

    :param utc_str: string of UTC
    :type utc_str: str, required
    :param loczone: specified location
    :type loczone: str, required
    """
    timezone = pytz.timezone(loczone)
    utc_dt=parser.isoparse(str(utc_str))
    d_loc = utc_dt.astimezone(timezone)
    return d_loc

def conv_from_pendulum(pendulum_dt):
    datetime_string = pendulum_dt.to_datetime_string()
    return datetime.fromisoformat(datetime_string)

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


def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days_ahead)

    #d = datetime.date(2011, 7, 2)
    #next_monday = next_weekday(d, 0) # 0 = Monday, 1=Tuesday, 2=Wednesday...
    #print(next_monday)