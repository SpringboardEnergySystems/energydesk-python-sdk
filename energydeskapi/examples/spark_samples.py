import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.spark.spark_api import SparkCli
from energydeskapi.types.company_enum_types import UserRoleEnum
from energydeskapi.sdk.datetime_utils import prev_weekday
from datetime import datetime
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])

def fetch_spark():
    sp=SparkCli()
    print(sp.fetch("orders"))


if __name__ == '__main__':
    api_conn = init_api()
    fetch_spark()
