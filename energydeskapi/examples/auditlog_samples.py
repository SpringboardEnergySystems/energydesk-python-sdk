import json
import logging
from energydeskapi.system.default_asset_types import initialize_default_etrm_assettypes
from energydeskapi.audit.audit_log_api import AuditLogApi
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.types.asset_enum_types import AssetCategoryEnum

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def get_audit_log_types(api_conn):
    jsondata = AuditLogApi.get_audit_log_types(api_conn)
    print(json.dumps(jsondata, indent=2))

def get_audit_log(api_conn):
    jsondata = AuditLogApi.get_audit_log( api_conn, {})
    print(json.dumps(jsondata, indent=2))

if __name__ == '__main__':

    api_conn = init_api()

    get_audit_log_types(api_conn)
    get_audit_log(api_conn)
