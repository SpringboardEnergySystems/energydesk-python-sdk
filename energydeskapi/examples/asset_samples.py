import json
import logging

from energydeskapi.assets.assets_api import AssetsApi
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.types.asset_enum_types import AssetTypeEnum

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def get_clearing_accounts(api_conn):
    jsondata = AssetsApi.get_assets_embedded(
        api_conn, {"asset_type": AssetTypeEnum.ACCOUNT.value})
    print(json.dumps(jsondata, indent=2))


def query_asset_info(api_conn):
    df = AssetsApi.get_asset_types(api_conn)
    print("Asset types", df)
    df = AssetsApi.get_assets_df(api_conn)
    print("Asset list", df)
    u = AssetsApi.get_asset_type_url(api_conn, 0)
    print(u)


if __name__ == '__main__':

    api_conn = init_api()
    get_clearing_accounts(api_conn)
