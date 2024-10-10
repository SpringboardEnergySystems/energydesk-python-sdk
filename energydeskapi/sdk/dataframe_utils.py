import json
from io import BytesIO
from typing import Union
import pytz
import typing
import pandas as pd
from datetime import datetime
from dateutil import parser
def text_to_dataframe(value: Union[bytes, None]) -> typing.Optional[pd.DataFrame]:
    if value is not None:
        io = BytesIO(value)
        dtypes = json.loads(io.readline())
        date_columns = [key for (key, value) in dtypes.items() if str(value).startswith("date")]
        return pd.read_csv(io, parse_dates=date_columns)
    else:
        return None


def dataframe_to_text(df: pd.DataFrame) -> str:
    dtypes = df.dtypes
    dtypes_json = dtypes.apply(lambda x: x.name).to_json()
    return "\n".join([dtypes_json, df.to_csv()])




def __datetime_valid(dt_str):
    if len(dt_str)<=10:
        return False
    if dt_str[10] == "_":
        return False
    try:
        parser.isoparse(dt_str)
    except:
        return False
    return True

def __check_return_utc_datetime(v):
    dt=None
    if isinstance(v, datetime):
        dt=v
    elif isinstance(v, str):
        if __datetime_valid(v):
            dt=parser.isoparse(v)
    return dt
def __check_convert_datetime(d, tz=None):
    if d.tzinfo is not None and d.tzinfo.utcoffset(d) is not None:
        d = d.astimezone(tz)
        return d
    else:
        if tz is None:
            tz=pytz.UTC
        d = tz.localize(d)
        d = d.astimezone(tz)
        return d
def convert_dataframe_to_json(df, active_tz=pytz.timezone("Europe/Oslo")):
    jsnlist=[]
    for index, row in df.iterrows():
        dictionary={}
        for col in df.columns.values:
            cval=row[col]
            dt=__check_convert_datetime(cval)
            if dt is not None:
                d=__check_return_utc_datetime(dt, active_tz)
                dictionary[str(col)] = d.strftime("%Y-%m-%d %H:%M:%S")
            else:
                dictionary[str(col)] = cval
        jsnlist.append(dictionary)
    return jsnlist