import json
import logging
import pandas as pd
from energydeskapi.profiles.profiles import PeriodProfile
from energydeskapi.sdk.common_utils import key_from_url
from energydeskapi.profiles.profiles_api import ProfilesApi
logger = logging.getLogger(__name__)



#  parse input profile
def parse_absolute_profile(xlfilepath):
    df = pd.read_excel(xlfilepath)
    df.columns = ["period_from", "period_until", "volume"]
    df["period_from"] = pd.to_datetime(df["period_from"])
    df["period_until"] = pd.to_datetime(df["period_until"])
    print(df)