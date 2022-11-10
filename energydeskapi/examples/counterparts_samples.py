import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.counterparts.counterparts_api import CounterPartsApi
from energydeskapi.types.asset_enum_types import AssetTypeEnum
from energydeskapi.types.market_enum_types import CommodityTypeEnum, InstrumentTypeEnum, MarketEnum
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])




def fetch_counterparts(api_conn):
    json_counterparts = CounterPartsApi.get_counterparts(api_conn)
    print(json_counterparts)
    ratings=CounterPartsApi.get_credit_ratings_df(api_conn)
    print(ratings)

def fetch_counterparts_df(api_conn):
    df = CounterPartsApi.get_counterparts_df(api_conn)
    print(df)

def register_counterparts(api_conn):
    payload = {'name': 'City of Oslo'}
    CounterPartsApi.upsert_counterparts(api_conn, payload)

def query_exposure(api_conn):
    res=CounterPartsApi.query_counterpart_exposure(api_conn, CommodityTypeEnum.GOs.value)
    print(res)


if __name__ == '__main__':

    api_conn=init_api()
    #register_counterparts(api_conn)
    query_exposure(api_conn)
