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
    register_asset_type(api_conn, "Hydro Power")
    register_asset_type(api_conn, "Wind Power")
    register_asset_type(api_conn, "Solar Power")
    register_asset_type(api_conn, "Hydro Pump")
    register_asset_type(api_conn, "Battery")
    register_asset_type(api_conn, "Consumption")
    register_asset_type(api_conn, "Cleared Account")
    register_asset_type(api_conn, "Bilateral Trades")


def initialize_default_flexibility_assettypes(api_conn):
    register_asset_type(api_conn, "Demand Response")
    register_asset_type(api_conn, "EV Charger")
    register_asset_type(api_conn, "Battery")
    register_asset_type(api_conn, "Wind Power")
    register_asset_type(api_conn, "Solar Power")

def initialize_default_dso_assettypes(api_conn):
    register_asset_type(api_conn, "Demand Response")
    register_asset_type(api_conn, "EV Charger")
    register_asset_type(api_conn, "Battery")
    register_asset_type(api_conn, "Transformer Station")
    register_asset_type(api_conn, "Sub Station")
    register_asset_type(api_conn, "Secondary Substation")
    register_asset_type(api_conn, "Congested Line")



def initialize_default_heatprod_assettypes(api_conn):
    register_asset_type(api_conn, "Fuels")
    register_asset_type(api_conn, "Electricity")
    register_asset_type(api_conn, "Heat Sales")
    register_asset_type(api_conn, "ElProduction")
    register_asset_type(api_conn, "Other")