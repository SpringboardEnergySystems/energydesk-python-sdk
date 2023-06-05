import json
import logging

from energydeskapi.assets.assets_api import AssetsApi, AssetType, Asset, AssetTechData
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.types.asset_enum_types import AssetCategoryEnum


def register_asset_type(api_conn, description):
    ast = AssetType()
    ast.pk = 0
    ast.description = description
    success, returned_data, status_code, error_msg = AssetsApi.upsert_asset_type(api_conn, ast)
    #print(success, returned_data, status_code, error_msg)

def initialize_default_etrm_assettypes(api_conn):
    register_asset_type(api_conn, "Production")
    register_asset_type(api_conn, "Consumption")
    register_asset_type(api_conn, "Cleared Account")
    register_asset_type(api_conn, "Bilateral Trades")