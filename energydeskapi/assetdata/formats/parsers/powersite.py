import pandas as pd
import pendulum
import pytz, io, logging
from energydeskapi.sdk.datetime_utils import conv_from_pendulum
logger = logging.getLogger(__name__)
def parse_timeseries(content:str):
    print("Parser for Eviny Powersite export")
    df = pd.read_csv(io.StringIO(content), sep=";")
    print(df.head(1000))
    df = df.rename(columns={"DateTime": "datetime", "Battery [kW]": "consumption"})
    df = df[["datetime", "consumption"]]
    def process_datetime(row):
        std = str(row["datetime"])
        if std.startswith("Asset Offline"):
            return None
        pt = pendulum.parse(std, tz="Europe/Oslo") # Assuming normal time as input
        pt = conv_from_pendulum(pt)
        row["datetime"]=pt
        row["consumption"] = float(row["consumption"].replace(",", "."))
        return row
    df = df.apply(process_datetime, axis=1)
    df['datetime'] = pd.to_datetime(df['datetime'], utc=True)
    df.index = df['datetime']
    df = df.tz_convert(tz=None)
    df = df.tz_localize(tz=pytz.timezone("UTC"))  # ,nonexistent='shift_forward',ambiguous='NaT')
    df = df.tz_convert(tz=pytz.timezone("Europe/Oslo"))
    df['datetime'] = df.index
    df['consumption'] = pd.to_numeric(df['consumption'], errors='coerce')
    df = df.dropna()
    return df