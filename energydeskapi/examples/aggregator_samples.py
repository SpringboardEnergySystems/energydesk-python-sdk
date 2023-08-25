import logging
from energydeskapi.system.default_asset_types import initialize_default_flexibility_assettypes
from energydeskapi.assets.assets_api import AssetsApi, AssetSubType, Asset, AssetTechData
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.types.asset_enum_types import AssetCategoryEnum
import pendulum
import json
from energydeskapi.customers.customers_api import CustomersApi
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])
logger = logging.getLogger(__name__)

def lookup_assettype_from_description(api_conn, description):
    df = AssetsApi.get_asset_types(api_conn, {'description': description})
    if len(df) == 0:
        return 0
    key = df.iloc[0]['pk']   # Assume no duplicates so pick first
    return int(key)

def register_individual_asset(description, external_id,
                              asset_manager_key, asset_owner_key, price_area,
                              meterpoint_id, geo_location,
                              asset_category=AssetCategoryEnum.PRODUCTION,
                              asset_type=1):
    a=Asset()
    at = AssetTechData()
    at.startup_date = str(pendulum.today())[:10]
    a.tech_data = at
    a.description=description
    a.extern_asset_id = external_id
    a.meter_id = meterpoint_id
    a.sub_meter_id = "-"
    a.asset_type = AssetsApi.get_asset_type_url(api_conn, asset_category)
    a.asset_category = AssetsApi.get_asset_category_url(api_conn, asset_type)
    a.asset_owner = CustomersApi.get_company_url(api_conn, asset_owner_key)
    a.asset_manager= CustomersApi.get_company_url(api_conn, asset_manager_key)
    a.price_area=price_area
    a.location = geo_location
    a.city="Bergen"
    a.address="Bergen"
    AssetsApi.create_assets(api_conn, [a])

def register_assets(api_conn):
    brreg_number_owner="922675163"
    brreg_number_manager = "922675163"
    asset_owner = CustomersApi.get_company_from_registry_number(api_conn, brreg_number_owner)
    asset_manager = CustomersApi.get_company_from_registry_number(api_conn, brreg_number_manager)
    register_individual_asset(description="Test Solar1", external_id="SOLAR_PANEL_456", asset_manager_key=asset_manager['pk'],
                              asset_owner_key=asset_owner['pk'],price_area="NO5",
                              meterpoint_id="77112312312", geo_location="60.603186775251324,9.07437258113459",
                              asset_category=AssetCategoryEnum.PRODUCTION,
                              asset_type=lookup_assettype_from_description(api_conn, "Solar Power")
                              )
    register_individual_asset(description="Test Solar2", external_id="SOLAR_PANEL_457", asset_manager_key=asset_manager['pk'],
                              asset_owner_key=asset_owner['pk'],price_area="NO5",
                              meterpoint_id="77112312311", geo_location="60.603186775251324,9.07437258113459",
                              asset_category=AssetCategoryEnum.PRODUCTION,
                              asset_type=lookup_assettype_from_description(api_conn, "Solar Power")
                              )

def view_assets(api_conn):
    # embedded means with subsets of data nested into outer json dict instead of URLs to related objects
    assets=AssetsApi.get_assets_embedded(api_conn)
    print(json.dumps(assets, indent=2))

if __name__ == '__main__':
    api_conn=init_api()
    initialize_default_flexibility_assettypes(api_conn)
    register_assets(api_conn)
    view_assets(api_conn)