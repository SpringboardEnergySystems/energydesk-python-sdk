import json
import logging

import pandas as pd

from energydeskapi.system.default_asset_types import initialize_default_etrm_assettypes
from energydeskapi.assets.assets_api import AssetsApi, AssetSubType, Asset, AssetTechData
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.types.asset_enum_types import AssetCategoryEnum
from energydeskapi.grid.grid_api import GridApi
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def resolve_mpids(api_conn):

    types = GridApi.get_gridmaps(api_conn)
    print(len(types))
    allrec=[]
    for i in range(len(types)):
        #print(types[i]['grid_map'])
        allrec.extend(types[i]['grid_map'])
    df=pd.DataFrame(data=allrec)
    print(df)

if __name__ == '__main__':

    api_conn = init_api()
    resolve_mpids(api_conn)