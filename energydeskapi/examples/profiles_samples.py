import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.sdk.profiles_utils import generate_normalized_profile
from energydeskapi.profiles.profiles_api import ProfilesApi, StoredProfile
from energydeskapi.profiles.profiles import GenericProfile
import pandas as pd
import pytz
import json
from energydeskapi.types.market_enum_types import CommodityTypeEnum
from energydeskapi.types.common_enum_types import get_month_list,get_weekdays_list
from energydeskapi.sdk.pandas_utils import get_winter_profile, get_workweek, get_weekend
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])




def load_profiles(api_conn):
    jsdata = ProfilesApi.get_volume_profiles(api_conn)
    print(jsdata)
    jsdata = ProfilesApi.get_volume_profile_by_key(api_conn, 1)
    print(jsdata)

def create_profile(api_conn):
    v=StoredProfile()
    v.profile={
        'monthly_profile': get_winter_profile(),
        'weekday_profile': get_workweek(),
        'daily_profile': list(range(8, 18))
    }
    v.description="winterprofile"
    jsres = ProfilesApi.upsert_volume_profile(api_conn, v)
    print(jsres)





def convert_volume_profile(api_conn):
    monthly_volume=[100000, 90000,80000,70000,60000,50000,50000,50000,60000,70000,80000,50000]
    weekly_volume=[4, 5, 6, 5, 3.5, 2.2, 1]
    hourly_volume=[3.355589041, 3.246328767, 3.186978022,3.161808219,3.164410959, 3.247890411, 3.533753425, 3.862465753,3.993753425, 4.026849315, 4.031589041, 3.996109589, 3.963972603, 3.922219178, 3.902849315, 3.915945205, 3.96309589, 3.965643836, 3.942986301, 3.909205479, 3.860849315, 3.781863014, 3.664438356,3.511753425]
    hourly_map={str(k): v for k, v in zip(list(range(24)), hourly_volume)}
    monthly_map = {k: v for  k, v in zip(get_month_list(), monthly_volume)}
    #monthly_map = {k: v/sum(monthly_volume) for  k, v in zip(get_month_list(), monthly_volume)}
    weekly_map = {k: v for  k, v in zip(get_weekdays_list(), weekly_volume)}

    volume_profile={
        'monthly_profile':monthly_map,
        'weekday_profile': weekly_map,
        'daily_profile':hourly_map
    }
    print(volume_profile)
    dprof=GenericProfile.from_dict(volume_profile)
    success, returned_data, status_code, error_msg = ProfilesApi.convert_relativeprofile_to_yearlyfactors(api_conn,2023,3, dprof)
    if success:
        dict=json.loads(returned_data['profile'])
        df=pd.DataFrame.from_dict(dict, orient='index')
        df.index = pd.to_datetime(df.index)
        df.index = df.index.tz_convert(pytz.timezone("Europe/Oslo"))
        df = df.rename(columns={df.columns[0]: 'hourly_factor'})
        print(df)
        # Pandas by default with to_json(ISO) converts to UTC.
        df.index=df.index.strftime("%Y-%m-%d %H:%M:%S+01:00")
        json_to_save=df.to_dict()
        #print(json_to_save)



if __name__ == '__main__':

    api_conn=init_api()
    convert_volume_profile(api_conn)
    #load_profiles(api_conn)
