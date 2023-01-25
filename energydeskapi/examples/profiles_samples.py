import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.profiles.profiles_api import ProfilesApi
from energydeskapi.types.market_enum_types import CommodityTypeEnum
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])




def load_profiles(api_conn):
    json_counterparts = ProfilesApi.get_volume_profiles(api_conn)
    print(json_counterparts)





if __name__ == '__main__':

    api_conn=init_api()
    load_profiles(api_conn)
