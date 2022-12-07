import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.counterparts.counterparts_api import CounterPartsApi, CounterPartLimit
from energydeskapi.types.market_enum_types import CommodityTypeEnum
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

def fetch_counterpart_limits(api_conn):
    parameters = {'company__id': 722}
    res = CounterPartsApi.get_counterpart_limits(api_conn, parameters)
    print(res)

def fetch_counterpart_limits_by_key(api_conn):
    pk = 1
    res = CounterPartsApi.get_counterpart_limits_by_key(api_conn, pk)
    print(res)

def register_counterpart_limits(api_conn):
    counterpart_limit = CounterPartLimit()
    counterpart_limit.pk = 0
    counterpart_limit.company = "http://127.0.0.1:8001/api/customers/companies/722/"
    counterpart_limit.valid_from_date = "2022-12-11"
    counterpart_limit.valid_until_date = "2022-12-24"
    counterpart_limit.volume_limit_mwh = "4.000"
    success, returned_data, status_code, error_msg = CounterPartsApi.upsert_counterpart_limits(api_conn, counterpart_limit)
    print(returned_data)


if __name__ == '__main__':

    api_conn=init_api()
    #register_counterparts(api_conn)
    #query_exposure(api_conn)
    fetch_counterpart_limits(api_conn)
    #fetch_counterpart_limits_by_key(api_conn)
    #register_counterpart_limits(api_conn)
