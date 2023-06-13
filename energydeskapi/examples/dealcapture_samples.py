import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.contracts.dealcapture import bilateral_dealcapture, get_dealcapture_config, set_dealcapture_config
import pandas as pd
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])

def fetch_dealcapture_config(api_conn):
    json_res = get_dealcapture_config(api_conn)
    print(json_res)

def save_dealcapture_config(api_conn):
    payload = {
                  "dealcapture_book_pk": 4,
                  "dealcapture_user": 1
                }
    result = set_dealcapture_config(api_conn, payload)
    print(result)

if __name__ == '__main__':
    api_conn=init_api()
    #bilateral_dealcapture(api_conn)
    save_dealcapture_config(api_conn)
    fetch_dealcapture_config(api_conn)
