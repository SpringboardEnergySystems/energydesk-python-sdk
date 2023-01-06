import pytz
from dateutil import parser

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

def convert_datime_to_utcstr(dt):
    dtutc=convert_timezone(dt)
    s_dt = dtutc.strftime('%Y-%m-%dT%H:%M:%S+00:00')
    return s_dt

def convert_datime_to_locstr(dt, loczone="Europe/Oslo"):
    dtutc=localize_datetime(dt, loczone)
    s_dt = dtutc.strftime('%Y-%m-%dT%H:%M:%S+00:00')
    return s_dt

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