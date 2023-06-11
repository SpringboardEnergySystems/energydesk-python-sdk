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
    print("Registered", success, description)
    #print(success, returned_data, status_code, error_msg)


def initialize_default_etrm_assettypes(api_conn):
    register_asset_type(api_conn, "Hydro Production")
    register_asset_type(api_conn, "Wind Production")
    register_asset_type(api_conn, "Solar Production")
    register_asset_type(api_conn, "Battery")
    register_asset_type(api_conn, "Consumption")
    register_asset_type(api_conn, "Cleared Account")
    register_asset_type(api_conn, "Bilateral Trades")


def initialize_default_heatprod_assettypes(api_conn):
    register_asset_type(api_conn, "Fuels")
    register_asset_type(api_conn, "Electricity")
    register_asset_type(api_conn, "Heat Sales")
    register_asset_type(api_conn, "Other")