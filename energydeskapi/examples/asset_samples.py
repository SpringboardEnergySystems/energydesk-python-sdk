import json
import logging
from energydeskapi.system.default_asset_types import initialize_default_etrm_assettypes
from energydeskapi.assets.assets_api import AssetsApi, AssetSubType, Asset, AssetTechData
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.types.asset_enum_types import AssetCategoryEnum

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def get_clearing_accounts(api_conn):
    jsondata = AssetsApi.get_assets_embedded(
        api_conn, {"asset_type": AssetCategoryEnum.TRADING_ACCOUNT.value})
    print(json.dumps(jsondata, indent=2))

def get_assets(api_conn):
    jsondata = AssetsApi.get_assets_embedded(
        api_conn)
    print(json.dumps(jsondata, indent=2))

def query_asset_info(api_conn):
    df = AssetsApi.get_asset_types(api_conn)
    print("Asset types", df)
    df = AssetsApi.get_assets_df(api_conn)
    print("Asset list", df)
    u = AssetsApi.get_asset_type_url(api_conn, 0)
    print(u)



def fetch_asset_categories(api_conn):
    result = AssetsApi.get_asset_categories(api_conn)
    print(result)
def fetch_asset_types(api_conn):
    result = AssetsApi.get_asset_types(api_conn)
    print(result)

def register_asset(api_conn):
    a = Asset()
    at = AssetTechData()
    a.pk = 101
    a.extern_asset_id = "Test asset 3"
    a.description = "Test asset 3"
    a.asset_type = "http://127.0.0.1:8001/api/assets/assettypes/1/"
    at.max_effect_mw = 2.0
    at.yearly_volume_mwh = 2.0
    at.elcert_support_percentage = 2.0
    at.licenced_until = "2023-03-30"
    at.startup_date = "2023-03-16"
    a.tech_data = at
    a.grid_connection = "http://127.0.0.1:8001/api/customers/companies/195/"
    a.power_supplier = "http://127.0.0.1:8001/api/customers/companies/721/"
    a.asset_owner = "http://127.0.0.1:8001/api/customers/companies/721/"
    a.asset_manager = "http://127.0.0.1:8001/api/customers/companies/721/"
    a.vendor = "test"
    a.meter_id = "test"
    a.sub_meter_id = "test"
    a.is_main_meter = True
    a.location = "63,10"
    a.price_area = "NO1"
    a.is_active = False
    success, returned_data, status_code, error_msg = AssetsApi.upsert_asset(api_conn, a)
    print(success, returned_data, status_code, error_msg)

def register_asset_subtype(api_conn):
    ast = AssetSubType()
    ast.pk = 0
    ast.description = "test subtype"
    success, returned_data, status_code, error_msg = AssetsApi.upsert_asset_subtypes(api_conn, ast)
    print(success, returned_data, status_code, error_msg)


if __name__ == '__main__':

    api_conn = init_api()
    #get_clearing_accounts(api_conn)
    #fetch_asset_subtypes(api_conn)
    #initialize_default_etrm_assettypes(api_conn)
    #fetch_asset_categories(api_conn)
    #fetch_asset_types(api_conn)
    get_assets(api_conn)
    #register_asset_subtype(api_conn)
    #query_asset_info(api_conn)
