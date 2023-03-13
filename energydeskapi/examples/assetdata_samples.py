import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.assets.assetdata_api import AssetDataApi

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def query_asset_info(api_conn):
    df = AssetDataApi.get_assetgroup_forecast_df(api_conn, [1, 2, 3])
    print(df)
    df = df.resample('MS').sum()
    df['period']=df.index
    print(df)


if __name__ == '__main__':

    api_conn = init_api()
    query_asset_info(api_conn)
