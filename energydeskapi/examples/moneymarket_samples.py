import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.moneymarkets.moneymarkets_api import MoneyMarketsApi
from energydeskapi.types.asset_enum_types import AssetTypeEnum
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])




def get_moneymarket_data(api_conn):
    #MoneyMarketsApi
    pass

def fetch_fxspot(api_conn):
    df = MoneyMarketsApi.get_fxspot(api_conn)
    print(df)

def fetch_fxtenors(api_conn):
    df = MoneyMarketsApi.get_fxtenors(api_conn)
    print(df)

def fetch_yieldcurves(api_conn):
    param = {"country": "NOK"}
    df = MoneyMarketsApi.get_yieldcurves(api_conn, param)
    print(df)


if __name__ == '__main__':

    api_conn=init_api()
    # get_moneymarket_data(api_conn)
    #fetch_fxspot(api_conn)
    fetch_fxtenors(api_conn)
    #fetch_yieldcurves(api_conn)
