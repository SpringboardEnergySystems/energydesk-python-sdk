import logging
from energydeskapi.sdk.common_utils import key_from_url
from energydeskapi.geolocation.location_api import LocationApi
from energydeskapi.gos.gos_api import GosApi
from energydeskapi.assets.assetgroup_utils import register_new_assetgroup
from energydeskapi.types.asset_enum_types import AssetCategoryEnum
from energydeskapi.assets.assets_api import AssetsApi, AssetSubType, Asset, AssetTechData
from energydeskapi.sdk.common_utils import init_api
import json
from energydeskapi.assets.asset_groups_api import AssetGroupApi, AssetGroup
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])




def get_areas(api_conn):
    # df=LocationApi.get_local_areas(api_conn, LocationTypeEnum.GOs_OFFER_AREA)
    #print("Loc area", df)
    def_json=LocationApi.get_default_zones(api_conn)
    print(def_json)
    return
    geomdata=LocationApi.generate_default_map(api_conn,map_type="COUNTRY",include_assets=True, zones=['NO4'], country="DNK")
    print(geomdata)

def load_dso(api_conn, name="elvia"):
    res=LocationApi.get_dso_area(api_conn, name)
    print(res)

def get_asset_geo(api_conn, name="Nedre Glomma"):
    res = AssetsApi.get_assets(api_conn, {'description': name})
    group_pk=res['results'][0]['pk']
    res=AssetGroupApi.get_asset_groups(api_conn, {'main_asset__id':group_pk})
    sub_asset_list=[]
    for r in res[0]['sub_assets']:
        sub_asset_list.append(int(key_from_url(r)))
    #res=LocationApi.get_dso_area(api_conn, name)
    print(sub_asset_list)
    res=LocationApi.generate_asset_polygon(api_conn, sub_asset_list)
    print(res)
if __name__ == '__main__':
    api_conn=init_api()
    load_dso(api_conn, "demodso")
