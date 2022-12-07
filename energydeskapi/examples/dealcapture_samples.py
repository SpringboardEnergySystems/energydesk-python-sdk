import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.contracts.dealcapture import bilateral_dealcapture
import pandas as pd
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


if __name__ == '__main__':
    api_conn=init_api()
    bilateral_dealcapture(api_conn)
