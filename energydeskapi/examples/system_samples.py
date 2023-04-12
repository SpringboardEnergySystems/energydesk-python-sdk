import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.system.system_api import SystemApi
from energydeskapi.types.company_enum_types import UserRoleEnum

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])

def fetch_system_features(api_conn):
    result = SystemApi.get_system_features(api_conn)
    print(result)

def fetch_system_access_types(api_conn):
    result = SystemApi.get_system_access_types(api_conn)
    print(result)


if __name__ == '__main__':
    api_conn = init_api()
    #fetch_system_features(api_conn)
    fetch_system_access_types(api_conn)
