import pendulum
import pandas as pd
import logging
import pytz
logger = logging.getLogger(__name__)
def parse_timeseries(content:str):
    try:
        def fix_datetime(row):
            sd = str(row['datetime'])
            dt = pendulum.parse(sd[6:10] + "-" + sd[3:5] + "-" + sd[0:2] + " " + sd[11:16] + ":00", tz="Europe/Oslo")
            return str(dt)

        def fix_metervals(row):
            sd = str(row['consumption'])
            sd = sd.replace(",", ".")
            sd = sd.replace(" ", "")
            return float(sd)

        df = pd.read_csv(content, delimiter=';')
        df = df.ffill()
        df = df.rename(columns={"Fra": "datetime", "KWH 60 Forbruk": "consumption"})
        df = df[["datetime", "consumption"]]
        df["datetime"] = df.apply(fix_datetime, axis=1)
        df["consumption"] = df.apply(fix_metervals, axis=1)
        df['datetime'] = pd.to_datetime(df['datetime'], utc=True)
        df.index = df['datetime']
        df = df.tz_convert(tz=None)
        df = df.tz_localize(tz=pytz.timezone("UTC"))  # ,nonexistent='shift_forward',ambiguous='NaT')
        df = df.tz_convert(tz=pytz.timezone("Europe/Oslo"))
        df['datetime'] = df.index
        return df
    except Exception as e:
        logger.error(e)
        return None