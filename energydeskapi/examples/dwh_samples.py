import json
import logging
from energydeskapi.system.default_asset_types import initialize_default_etrm_assettypes
from energydeskapi.audit.audit_log_api import AuditLogApi
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.types.asset_enum_types import AssetCategoryEnum
import pandas as pd
from energydeskapi.dwh.dwh_api import DwhApi
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])



def get_contracts(api_conn):
    jsondata = DwhApi.get_contract_dimension( api_conn, {})
    #print(json.dumps(jsondata, indent=2))
    df=pd.DataFrame(jsondata)
    print(df)


if __name__ == '__main__':

    api_conn = init_api()

    get_contracts(api_conn)

