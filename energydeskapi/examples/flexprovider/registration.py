import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.energydesk.general_api import GeneralApi
from energydeskapi.flexibility.dso_api import DsoApi
from energydeskapi.assets.assets_api import AssetsApi
from energydeskapi.sdk.profiles_utils import get_baseload_profile, get_default_availability_profile
from energydeskapi.types.flexibility_enum_types import AssetProfileTypeEnums
from energydeskapi.flexibility.flexibility_api import FlexibilityApi, ExternalMarketAsset
import pendulum
import json
import pandas as pd
import os
from energydeskapi.assetdata.baselines_utils import BaselinesModelsEnums, initialize_standard_algorithms, create_default_algo_parameters
import glob
import random
import sys
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])




def register_meterdata_for_asset(api_conn, mpid, df):
    existing = FlexibilityApi.lookup_asset_registration_by_mpid(api_conn, mpid)
    if len(existing['results'])==0:
        logging.info("Cannot register meterdata for asset {}".format(mpid))
        return
    logging.info("Registering meter data for asset {}".format(mpid))
    result=FlexibilityApi.register_asset_readings(api_conn, existing['results'][0]['pk'], df)
    if result is not None:
        logging.info("Registered data")

def generate_baseline(mpid):
    existing = FlexibilityApi.lookup_asset_registration_by_mpid(api_conn, mpid)
    if len(existing['results'])==0:
        logging.info("Cannot register meterdata for asset {}".format(mpid))
        return
    params = create_default_algo_parameters(BaselinesModelsEnums.BUSINESSDAY_PROFILE)
    params.extra_parameter1 = "7"
    params.periods_predicted = 14
    payload = {
        'asset_id': existing['results'][0]['pk'],
        'algorithm_code': BaselinesModelsEnums.BUSINESSDAY_PROFILE.name,
        'algorithm_parameters': params.json
    }
    print(payload)
    outdata=FlexibilityApi.generate_baselines_for_asset(api_conn,payload)
    df_base=pd.DataFrame(data=outdata)
    print(df_base)




def register_availability_profile(api_conn, description:str, hours=[6, 13,19],half_cpacity=[16,17,18]):
    prof=get_default_availability_profile()
    prof['weekday_profile'][4] = 0
    prof['weekday_profile'][5] = 0
    for x in prof['daily_profile']:
        if x in half_cpacity:
            prof['daily_profile'][x] = 0.5
        elif x not in hours:
            prof['daily_profile'][x]=0
    type_url=FlexibilityApi.get_asset_profile_type_url(api_conn, AssetProfileTypeEnums.RELATIVE)
    payload={'profile_name':description,'profile_type':type_url, 'profile':prof}
    #print(payload)
    # Store it as a template
    #success, returned_data, status_code, error_msg=FlexibilityApi.upsert_availability_profile_template(api_conn, 0, payload)
    # View templates for user
    #templates=FlexibilityApi.get_availability_profile_templates(api_conn)

    # Store it on Asset table to be linked to concrete asset offer
    success, returned_data, status_code, error_msg=FlexibilityApi.upsert_asset_availability_profile(api_conn, 0, payload)
    #print(status_code)
    return returned_data # Profile object to be saved on asset_availabiolity

def register_flex_availability(api_conn, extern_asset_id,
                               period_from,period_until, kw_max=200, profile_name="Demo profile"):
    profile=register_availability_profile(api_conn, profile_name)
    profile_url=FlexibilityApi.get_asset_availability_profile_url(api_connection=api_conn, pk=profile['pk'])
    outdata=FlexibilityApi.register_asset_availability(api_conn,extern_asset_id=extern_asset_id,
                                               period_from=str(period_from), period_until=str(period_until),
                                               availability_profile=profile_url, kw_available=kw_max)

def register_flexible_asset(api_conn, asset_row):
    extern_asset_id=asset_row['Name']   # FSP provider's own identifier. For simplicity Name is used here
    end_customer_name = asset_row['Customer']
    address = asset_row['Address']
    meterpoint_id = asset_row['MPID']
    latitude = asset_row['Latitude']
    longitude = asset_row['Longitude']
    manager=asset_row['FSP Company Regnumber']
    existing=FlexibilityApi.lookup_asset_registration(api_conn, extern_asset_id)
    if len(existing['results'])>0:
        logging.info("Asset {} managed by {} is already registered".format(extern_asset_id, manager))
        return
    logging.info("Now registering Asset {} ".format(extern_asset_id))
    outdata=FlexibilityApi.register_flexible_asset(api_conn, extern_asset_id=extern_asset_id,
                                                   description=extern_asset_id,
                                                   meter_id=meterpoint_id,
                                                   sub_meter_id="",
                                                   address=address,
                                                   city="Oslo",
                                                   latitude=float(latitude),
                                                   longitude=float(longitude),
                                                   asset_category="CONSUMPTION",
                                                   asset_type="Elkjele",
                                                   asset_owner_regnumber=manager,
                                                   asset_manager_regnumber=manager,
                                                   dso_regnumber="980489698",
                                                   brp_company_regnumber="876944642",
                                                   callback_url="http://127.0.0.1:8090/callback"
                                           )


def load_asset_availability_schedule(api_conn, extern_asset_id):
    found=AssetsApi.get_assets(api_conn, {'extern_asset_id':extern_asset_id})
    if len(found['results'])==0:
        return None
    name=found['results'][0]['description']
    t1 = pendulum.today(tz="Europe/Oslo")
    t2 = t1.add(days=5)   # Cast to string to get ISO format
    outdata=FlexibilityApi.get_availability_schedule(api_conn,extern_asset_id=extern_asset_id,
                                                     period_from=str(t1),period_until=str(t2))
    df=pd.DataFrame(outdata['schedule'])
    print(df)

def load_asset_dispatch_schedule(api_conn, extern_asset_id):
    found=AssetsApi.get_assets(api_conn, {'extern_asset_id':extern_asset_id})
    if len(found['results'])==0:
        return None
    name=found['results'][0]['description']
    t1 = pendulum.today(tz="Europe/Oslo")
    t2 = t1.add(days=5)   # Cast to string to get ISO format
    outdata=FlexibilityApi.get_asset_dispatch_schedule(api_conn,extern_asset_id=extern_asset_id,
                                                     period_from=str(t1),period_until=str(t2))
    df=pd.DataFrame(outdata)
    print(df)

def load_available_flexibility(api_conn, extern_asset_id=None):
    param={}
    if extern_asset_id is not None:
        param['asset__extern_asset_id']=extern_asset_id

    data=FlexibilityApi.get_flexible_assets_embedded(api_conn, param)
    for fa in data['results']:
        print(json.dumps(fa, indent=2))

def load_assets_from_file(filename="./assets_sample.xlsx"):
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    filename = os.path.join(__location__, filename)
    df = pd.read_excel(filename)
    return df

def load_assetmeterdata_from_files(specific_mpid="707057500057530000", specific_file="sample_meterdata.xlsx"):
    mp={}
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__), "meterdata"))

    if specific_mpid =="707057500057530000" : # The sample
        filename = os.path.join(__location__, specific_file)
        df = pd.read_excel(filename)
        df['datetime'] = pd.to_datetime(df[df.columns[0]])
        df['consumption'] = df[df.columns[1]]
        mp[specific_mpid]=df
    else:
        for j in glob.glob(__location__ + "/*.xlsx"):
            cols = j.split("-")
            if len(cols)<4:
                continue
            filename = os.path.join(j)
            df = pd.read_excel(j)
            mpid=cols[3].strip()
            df['datetime'] = pd.to_datetime(df[df.columns[0]])
            df['consumption'] =df[df.columns[1]]
            mp[mpid]=df

    return mp

def show_availability(api_conn):
    for a in AssetsApi.get_assets(api_conn)['results']:
        load_asset_availability_schedule(api_conn, a['extern_asset_id'])

def show_dispatch_schedule(api_conn):
    for a in AssetsApi.get_assets(api_conn)['results']:
        load_asset_dispatch_schedule(api_conn, a['extern_asset_id'])
        break

def show_registered_assets(api_conn):
    data=FlexibilityApi.get_offered_assets(api_conn)
    print(data)
    for d in data['results']:
        exist=d['pk']
        if len(d['external_market_offerings'])==0:
            print("Not yet offered externally")
            nodes_asset=ExternalMarketAsset(exist, "1234")
            FlexibilityApi.upsert_market_offering(api_conn, nodes_asset)
        else:
            logging.info("Asset already offered")

    FlexibilityApi.remove_market_offering(api_conn, "123asset")


def register_profile_on_all_assets(api_conn):
    assets = AssetsApi.get_assets(api_conn)
    counter=1
    for idx, a in enumerate(assets['results']):
        if idx!=1:
            continue

        # Next step is to make sure there exist a FlexibleAsset object for this asset

        # And refer to callback API for dispatch messages
        success, returned_data, status_code, error_msg=FlexibilityApi.upsert_flexible_asset(api_conn, a['extern_asset_id'], callback="https://127.0.0.1")
        if success:
            print("Got registration {}".format(returned_data))
        else:
            print("Failed to register flex asset {}".format(error_msg))
            continue

        days = int(random.uniform(80, 160))
        kwflex = int(random.uniform(80, 160))
        t1 = pendulum.today(tz="Europe/Oslo")
        t2 = t1.add(days=days)

        register_flex_availability(api_conn, a['extern_asset_id'], t1, t2, kwflex, "Demo profile " + str(counter))
        counter=counter+1


if __name__ == '__main__':
    api_conn=init_api()
    register_profile_on_all_assets(api_conn)
    #load_available_flexibility(api_conn)
    #show_availability(api_conn)
    #show_dispatch_schedule(api_conn)
