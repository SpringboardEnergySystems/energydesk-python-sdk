import logging
from energydeskapi.system.default_asset_types import initialize_default_flexibility_assettypes
from energydeskapi.assets.assets_api import AssetsApi, AssetSubType, Asset, AssetTechData
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.types.asset_enum_types import AssetCategoryEnum
import pendulum
from energydeskapi.flexibility.flexibility_api import FlexibilityApi
from energydeskapi.assetdata.baselines_api import BaselinesApi
from energydeskapi.types.contract_enum_types import QuantityTypeEnum, QuantityUnitEnum
from energydeskapi.assetdata.baselines_utils import initialize_standard_algorithms, create_default_algo_parameters
import pandas as pd
import sys
from energydeskapi.types.common_enum_types import PeriodResolutionEnum
from energydeskapi.types.asset_enum_types import TimeSeriesTypesEnum
from energydeskapi.types.baselines_enum_types import BaselinesModelsEnums
from energydeskapi.assetdata.assetdata_api import AssetDataApi
from energydeskapi.sdk.datetime_utils import conv_from_pendulum
from energydeskapi.sdk.pandas_utils import make_empty_timeseries_df
import json
from energydeskapi.customers.customers_api import CustomersApi
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])
logger = logging.getLogger(__name__)

import random
def generate_hourly_samples(period_from, period_until, basis, volatility):
    df=make_empty_timeseries_df(conv_from_pendulum(period_from),
                                conv_from_pendulum(period_until),
                                "H", timezone="Europe/Oslo")
    df['value']=0
    def create_value(row):  #Higher consumption in middle of day
        if row.name.hour<8:
            adj_basis=basis*0.8
        elif row.name.hour<18:
            adj_basis=basis*1.10
        else:
            adj_basis=basis*0.9
        v=adj_basis+random.uniform(-volatility, volatility)
        return v
    df['value']=df.apply(create_value, axis=1 )

    # First setting equal to index, then reformatting
    df['timestamp']=pd.to_datetime(df.index)
    df['date'] = pd.to_datetime(df.index)
    df['timestamp']=df['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%S+00:00')
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    return df



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

def generate_timeseries(api_conn, asset_pk):
    df=generate_hourly_samples(pendulum.today().add(days=-200),
                            pendulum.today(), 100, 12)
    payload = {
        'asset': AssetsApi.get_asset_url(api_conn, int(asset_pk)),
        'time_series_type': AssetDataApi.get_timeseries_type_url(api_conn, TimeSeriesTypesEnum.METERREADINGS),
        'quantity_unit': AssetDataApi.get_timeseries_value_unit_url(api_conn, QuantityUnitEnum.KW),
        'quantity_type': AssetDataApi.get_timeseries_value_type_url(api_conn, QuantityTypeEnum.EFFECT),
        'data': df.to_json(orient='records'),
        'last_updated': str(pendulum.now('Europe/Oslo')),
    }
    res, x, y, z = AssetDataApi.upsert_timeseries(api_conn, payload)
    print(res)

def simulate_meter_data(api_conn):
    assets = AssetsApi.get_assets_embedded(api_conn)
    for a in assets['results']:
        generate_timeseries(api_conn, a['pk'])

def generate_baselines_for_asset(api_conn, asset_id):
    params=create_default_algo_parameters(BaselinesModelsEnums.BUSINESSDAY_PROFILE)
    params.periods_predicted=5
    payload={
        'asset_id' : asset_id,
        'algorithm_code' : BaselinesModelsEnums.BUSINESSDAY_PROFILE.name,
        'algorithm_parameters': params.json
    }
    BaselinesApi.generate_baselines(api_conn, payload)

def generate_baselines(api_conn):
    assets = AssetsApi.get_assets_embedded(api_conn)
    for a in assets['results']:
        generate_baselines_for_asset(api_conn, a['pk'])
def display_basline_models(api_conn):

    res=BaselinesApi.get_baseline_algorithms(api_conn)
    print(res)
    res=BaselinesApi.get_baseline_resolutions(api_conn)
    print(res)
    initialize_standard_algorithms(api_conn)
    res=BaselinesApi.get_baseline_algorithminstances(api_conn)
    print(res)

def get_baselines_for_asset(api_conn, asset_pk): # Read back baselines from API
    params={
        'assetlist_id__in':[asset_pk],
        'time_series_type__id':TimeSeriesTypesEnum.BASELINES.value,
        'resolution': PeriodResolutionEnum.HOURLY.value
    }
    res = AssetDataApi.get_asset_timeseries(api_conn, params)
    print(res)
    df=pd.DataFrame(data=json.loads(res))
    print(df)

def get_baselines(api_conn): # Read back baselines from API
    assets = AssetsApi.get_assets_embedded(api_conn)
    for a in assets['results']:
        get_baselines_for_asset(api_conn, a['pk'])


def battery_map(val):
    color = 'darkgreen'# if val=="PRODUCING" else 'darkgreen'
    if val == "PRODUCING":
        color="navy"
    if val == "CONSUMING":
        color="darkred"
    return 'color:white; background-color: %s' % color
def dispatch_scheulder(api_conn): # Read back baselines from API
    jres=FlexibilityApi.get_empty_dispatch_schedule(api_conn)
    df=pd.DataFrame(data=json.loads(jres))
    print(df)
    sd =df[['state', 'date', 'time']].set_index(['date', 'time']).unstack().swaplevel(0, 1,axis=1).T.style.background_gradient(cmap='ocean_r').applymap(battery_map)
    print(df[['state', 'date', 'time']].set_index(['date', 'time']).unstack().swaplevel(0, 1,axis=1).T)
    print(sd.to_html())

if __name__ == '__main__':
    api_conn=init_api()
    dispatch_scheulder(api_conn)
    sys.exit(0)
    initialize_default_flexibility_assettypes(api_conn)
    register_assets(api_conn)
    view_assets(api_conn)
    simulate_meter_data(api_conn)
    display_basline_models(api_conn)
    # Ask server to generate Baseline. Alternative is to do locally and send to server as time series
    generate_baselines(api_conn)
    get_baselines(api_conn)




