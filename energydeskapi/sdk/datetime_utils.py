from datetime import datetime, timedelta, timezone
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