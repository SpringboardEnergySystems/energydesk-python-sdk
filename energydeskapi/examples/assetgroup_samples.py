import json
import logging

from energydeskapi.assets.assets_api import AssetsApi, AssetSubType, Asset, AssetTechData
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.assets.asset_groups_api import AssetGroupApi, AssetGroup
from energydeskapi.types.asset_enum_types import AssetTypeEnum

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def register_grouped_asset(api_conn, group, sub_assets):
    sub=sub_assets[0]
    sample=AssetsApi.get_asset_by_key(api_conn, sub['pk'])
    a = Asset()
    at = AssetTechData()
    a.pk = 0
    a.extern_asset_id = "Asset Group" + " - " + str(group)
    a.description = a.extern_asset_id
    a.tech_data=at
    a.asset_type = AssetsApi.get_asset_type_url(api_conn,10)
    a.grid_connection = sample['grid_connection']
    a.power_supplier = sample['power_supplier']
    a.asset_owner = sample['asset_owner']
    a.asset_manager = sample['asset_manager']
    a.vendor = sub['vendor']
    a.location = sub['location']
    a.price_area = sub['price_area']
    a.is_active = True
    #print(a.get_dict())
    success, returned_data, status_code, error_msg = AssetsApi.upsert_asset(api_conn, a)
    #print(returned_data)
    ag=AssetGroup()
    ag.description="Asset Group" + " - " + str(group)
    ag.main_asset=returned_data['pk']
    for sub in sub_assets:
        ag.sub_assets.append(sub['pk'])
    print(ag.get_dict(api_conn))
    AssetGroupApi.upsert_asset_group(api_conn, ag)



def register_asset_groups(api_conn):
    groups={}
    jsondata = AssetsApi.get_assets_embedded(
        api_conn)
    for a in jsondata['results']:
        if a['asset_type']['pk']==10:
            continue
        key=a['asset_type']['description']
        if  key not in groups:
            groups[key]=[]
        groups[key].append(a)

    for key in groups.keys():
        register_grouped_asset(api_conn, key, groups[key])


if __name__ == '__main__':

    api_conn = init_api()
    register_asset_groups(api_conn)

