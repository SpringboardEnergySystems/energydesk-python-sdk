import json
import logging

from energydeskapi.assets.assets_api import AssetsApi, AssetSubType, Asset, AssetTechData
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.assets.asset_groups_api import AssetGroupApi, AssetGroup
from energydeskapi.sdk.common_utils import key_from_url
from energydeskapi.assets.assetgroup_utils import register_new_assetgroup
from energydeskapi.types.asset_enum_types import AssetCategoryEnum
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])



def list_assets_of_type(api_conn, tp=AssetCategoryEnum.PRODUCTION.value):
    context={}
    res=AssetsApi.get_assets(api_conn, {'asset_category':AssetCategoryEnum.PRODUCTION.value, 'page_size':100})
    asset_list=[]
    for asset in res['results']:
        print(asset['pk'], asset['description'])
        asset_list.append((asset['pk'], asset['description']))  #List of tuples with key and description
    context['assets'] =asset_list

from energydeskapi.assets.asset_groups_api import AssetGroupApi, AssetGroup

def list_asset_groups(api_conn, tp=AssetCategoryEnum.GROUPED_ASSET.value):
    res=AssetGroupApi.get_asset_groups_embedded(api_conn, {'asset_type':AssetCategoryEnum.GROUPED_ASSET.value, 'page_size':100})
    sub_asset_list=[]
    for rec in res:
        print(rec['pk'], rec['description'])



def create_special_group(api_conn):
    jsondata = AssetsApi.get_assets_embedded(
        api_conn, {"asset_category": AssetCategoryEnum.PRODUCTION.value, 'page_size':1000})
    sub_asset_list=[]
    for rec in jsondata['results']:
        if rec['description'].startswith("B"):
            sub_asset_list.append(rec)
    register_new_assetgroup(api_conn,"B List", sub_asset_list)

def delete_asset_groups(api_conn):
    res=AssetGroupApi.get_asset_groups_embedded(api_conn, {'asset_type':AssetCategoryEnum.GROUPED_ASSET.value, 'page_size':100})
    sub_asset_list=[]
    for rec in res:
        print(rec['pk'], rec['description'])
        AssetGroupApi.delete_asset_group(api_conn, rec['pk'])
        mn=rec['main_asset']
        print(mn['pk'], mn['description'])
        AssetsApi.delete_asset(api_conn, mn['pk'])

def del_asset_group(api_conn):
    pk = 4
    result = AssetGroupApi.delete_asset_group(api_conn, pk)
    print(result)

def register_grouped_asset(api_conn, group, sub_assets):
    sub=sub_assets[0]
    sample=AssetsApi.get_asset_by_key(api_conn, sub['pk'])
    a = Asset()
    at = AssetTechData()
    a.pk = 0
    a.extern_asset_id = "Hydro Assets" + " - " + str(group)
    a.description = a.extern_asset_id
    a.tech_data=at
    a.asset_type = AssetsApi.get_asset_type_url(api_conn,AssetCategoryEnum.GROUPED_ASSET.value)
    a.grid_connection = sample['grid_connection']
    a.power_supplier = sample['power_supplier']
    a.asset_owner = sample['asset_owner']
    a.asset_manager = sample['asset_manager']
    a.vendor = sub['vendor']
    a.location = sub['location']
    a.price_area = sub['price_area']
    a.is_active = True
    success, returned_data, status_code, error_msg = AssetsApi.upsert_asset(api_conn, a)
    ag=AssetGroup()
    ag.description="Hydro Assets" + " - " + str(group)
    ag.main_asset=returned_data['pk']
    for sub in sub_assets:
        ag.sub_assets.append(sub['pk'])
    print(ag.get_dict(api_conn))
    AssetGroupApi.upsert_asset_group(api_conn, ag)



def register_asset_groups(api_conn):
    groups={}
    jsondata = AssetsApi.get_assets_embedded(
        api_conn, {'page_size':200})
    for a in jsondata['results']:
        if a['asset_type']['pk']!=AssetTypeEnum.HYDRO.value:
            continue
        price_area=a['price_area']
        if  price_area not in groups:
            groups[price_area]=[]
        groups[price_area].append(a)
    for key in groups.keys():
        register_grouped_asset(api_conn, key, groups[key])


if __name__ == '__main__':

    api_conn = init_api()
    #register_asset_groups(api_conn)
    #delete_asset_groups(api_conn)
    #list_asset_groups(api_conn)
    create_special_group(api_conn)

