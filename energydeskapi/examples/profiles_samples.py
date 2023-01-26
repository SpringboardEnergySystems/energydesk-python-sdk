import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.profiles.profiles_api import ProfilesApi, VolumeProfile
from energydeskapi.types.market_enum_types import CommodityTypeEnum
from energydeskapi.sdk.pandas_utils import get_winter_profile, get_workweek, get_weekend
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])




def load_profiles(api_conn):
    jsdata = ProfilesApi.get_volume_profiles(api_conn)
    print(jsdata)

def create_profile(api_conn):
    v=VolumeProfile()
    v.profile={
        'monthly_profile': get_winter_profile(),
        'weekday_profile': get_workweek(),
        'daily_profile': list(range(8, 18))
    }
    v.description="winterprofile"
    jsres = ProfilesApi.upsert_volume_profile(api_conn, v)
    print(jsres)


if __name__ == '__main__':

    api_conn=init_api()
    #create_profile(api_conn)
    load_profiles(api_conn)
