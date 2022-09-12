import sys
import requests
import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.energydesk.general_api import GeneralApi

import json

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])




def fetch_ticker(api_conn):
    text=GeneralApi.get_ticker_text(api_conn)
    print("To be shown in portal ", text)






if __name__ == '__main__':

    api_conn=init_api()
    fetch_ticker(api_conn)

