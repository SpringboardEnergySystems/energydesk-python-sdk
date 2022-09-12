import sys

import requests
import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.treasury.treasury_api import TreasuryApi

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])




def list_banks(api_conn):
    df=TreasuryApi.register_treasury_bank(api_conn, "880824872", "SWEDDDDDBANK")
    #df=TreasuryApi.get_treasury_banks(api_conn)
    print(df)


if __name__ == '__main__':

    api_conn=init_api()
    list_banks(api_conn)
