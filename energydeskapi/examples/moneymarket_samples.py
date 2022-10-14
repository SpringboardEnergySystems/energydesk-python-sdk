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


if __name__ == '__main__':

    api_conn=init_api()
    get_moneymarket_data(api_conn)
