import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.assets.assets_api import AssetsApi
from energydeskapi.types.asset_enum_types import AssetTypeEnum
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])




def query_asset_info(api_conn):
    df=AssetsApi.get_asset_types(api_conn)
    print("Asset types", df)
    #df=AssetsApi.get_assets_ext(api_conn)
    #print("Asset list", df)
    u=AssetsApi.get_asset_type_url(api_conn, AssetTypeEnum.HYDRO)
    print(u)


if __name__ == '__main__':

    api_conn=init_api()
    query_asset_info(api_conn)
