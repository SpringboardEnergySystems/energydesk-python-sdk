import json
import logging

from energydeskapi.assets.assets_api import AssetsApi, AssetSubType, Asset, AssetTechData
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.assets.asset_groups_api import AssetGroupApi, AssetGroup
from energydeskapi.types.asset_enum_types import AssetCategoryEnum
from energydeskapi.sdk.common_utils import key_from_url
from energydeskapi.assetdata.assetdata_api import AssetDataApi
logger = logging.getLogger(__name__)


#  Sub assets are on dictionary format as returned by AssetsApi.get_assets_embedded(api_conn, {'page_size':200})
def register_new_assetgroup(api_conn, group_name, sub_assets=[]):
    sub=sub_assets[0]
    sample=AssetsApi.get_asset_by_key(api_conn, sub['pk'])  #Use the first sub asset member as default for common data
    a = Asset()
    at = AssetTechData()
    a.pk = 0
    a.extern_asset_id =  str(group_name)
    a.description = a.extern_asset_id
    print(sub['asset_category'])
    atp=sub['asset_type']['pk']  #Asset type of sub asset -  Use as default for group
    a.tech_data=at
    a.asset_type=AssetsApi.get_asset_type_url(api_conn,int(atp))
    a.asset_category = AssetsApi.get_asset_category_url(api_conn,AssetCategoryEnum.GROUPED_ASSET.value)
    a.grid_connection = sample['grid_connection']
    a.power_supplier = sample['power_supplier']
    a.asset_owner = sample['asset_owner']
    a.asset_manager = sample['asset_manager']
    a.vendor = sub['vendor']
    a.address = sub['address']
    a.city = sub['city']
    a.location = sub['location']
    a.price_area = sub['price_area']
    a.is_active = True
    #Register a basic Asset object representing the Group
    success, returned_data, status_code, error_msg = AssetsApi.upsert_asset(api_conn, a)
    ag=AssetGroup()
    ag.description= str(group_name)
    ag.main_asset=returned_data['pk']
    for sub in sub_assets:
        ag.sub_assets.append(sub['pk'])
    print(ag.get_dict(api_conn))
    success, returned_data, status_code, error_msg=AssetGroupApi.upsert_asset_group(api_conn, ag)
    return success, returned_data, status_code, error_msg