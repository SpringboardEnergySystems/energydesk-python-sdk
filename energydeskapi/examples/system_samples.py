import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.system.system_api import SystemApi
from energydeskapi.types.company_enum_types import UserRoleEnum
from energydeskapi.sdk.datetime_utils import prev_weekday
from datetime import datetime
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])

def fetch_system_features(api_conn):
    result = SystemApi.get_system_features(api_conn)
    print(result)

def fetch_system_feature_by_key(api_conn):
    pk = 2
    result = SystemApi.get_system_feature_by_key(api_conn, pk)
    print(result)

def fetch_system_access_types(api_conn):
    result = SystemApi.get_system_access_types(api_conn)
    print(result)

def fetch_system_access_type_by_key(api_conn):
    pk = 2
    result = SystemApi.get_system_access_type_by_key(api_conn, pk)
    print(result)

def get_sysmanager_info(api_conn):
    result = SystemApi.get_system_manager(api_conn)
    print(result)
    SystemApi.upsert_system_manager(api_conn, 195, 721)

def test_weekday():
    x=prev_weekday(datetime.today(),0)
    print(x)

from energydeskapi.system.default_asset_types import initialize_default_etrm_assettypes
from energydeskapi.system.default_user_groups import initialize_default_usergroups
def update_system_defaults(api_conn):
    initialize_default_etrm_assettypes(api_conn)
    initialize_default_usergroups(api_conn)

if __name__ == '__main__':
    api_conn = init_api()
    #fetch_system_features(api_conn)
    #fetch_system_feature_by_key(api_conn)
    #fetch_system_access_types(api_conn)
    update_system_defaults(api_conn)
    #get_sysmanager_info(api_conn)
