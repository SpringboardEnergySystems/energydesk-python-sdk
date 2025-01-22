import json
import logging

import pandas as pd

from energydeskapi.system.default_asset_types import initialize_default_etrm_assettypes
from energydeskapi.assets.assets_api import AssetsApi, AssetSubType, Asset, AssetTechData
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.types.asset_enum_types import AssetCategoryEnum
from energydeskapi.contracts.fees_api import FeesApi
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def get_fees(api_conn):


    feerates = FeesApi.get_feerates(api_conn)
    print(feerates)
    feerates = FeesApi.get_feerates_embedded(api_conn)
    print(feerates)

if __name__ == '__main__':

    api_conn = init_api()
    get_fees(api_conn)