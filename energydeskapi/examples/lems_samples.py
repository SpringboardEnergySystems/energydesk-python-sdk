import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.lems.lems_api import LemsApi
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])




def get_market_status(api_conn):
    res=LemsApi.get_market_status(api_conn)
    print(res)


if __name__ == '__main__':

    api_conn=init_api()
    get_market_status(api_conn)

