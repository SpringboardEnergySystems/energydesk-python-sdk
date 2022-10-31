import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.counterparts.counterparts_api import CounterPartsApi
from energydeskapi.types.asset_enum_types import AssetTypeEnum
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])




def fetch_counterparts(api_conn):
    json_counterparts = CounterPartsApi.get_counterparts(api_conn)
    print(json_counterparts)

def fetch_counterparts_df(api_conn):
    df = CounterPartsApi.get_counterparts_df(api_conn)
    print(df)


if __name__ == '__main__':

    api_conn=init_api()
    fetch_counterparts(api_conn)
    #fetch_counterparts_df(api_conn)
