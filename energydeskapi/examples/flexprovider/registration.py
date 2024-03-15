import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.energydesk.general_api import GeneralApi
from energydeskapi.flexibility.dso_api import DsoApi
from energydeskapi.flexibility.flexibility_api import FlexibilityApi, ExternalMarketAsset
import pendulum
import json
import pandas as pd
import os
from energydeskapi.assetdata.baselines_utils import BaselinesModelsEnums, initialize_standard_algorithms, create_default_algo_parameters
import glob
import random
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

def register_flex_availability(api_conn, asset_row, crontab="0 11-13 * * 1-5"):
    extern_asset_id = asset_row['Name']
    t1 = pendulum.today(tz="Europe/Oslo")
    t2 = t1.add(days=30)   # Cast to string to get ISO format

       # 11 12 and 13 monday-friday

    outdata=FlexibilityApi.register_asset_availability(api_conn,extern_asset_id=extern_asset_id,
                                               period_from=str(t1), period_until=str(t2),
                                               crontab=crontab, kw_available=200)
    print(outdata)

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
    print(outdata)






def check_schedule(api_conn, asset_row):
    extern_asset_id = asset_row['Name']
    t1 = pendulum.today(tz="Europe/Oslo")
    t2 = t1.add(days=30)   # Cast to string to get ISO format
    outdata=FlexibilityApi.get_availability_schedule(api_conn,extern_asset_id=extern_asset_id,
                                                     period_from=str(t1),period_until=str(t2))
    print(outdata)

def load_assets_from_file(filename="./assets_sample.xlsx"):
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    filename = os.path.join(__location__, filename)
    df = pd.read_excel(filename)
    print(df)

    return df

def load_assetmeterdata_from_files(specific_mpid="707057500057530000", specific_file="sample_meterdata.xlsx"):
    mp={}
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__), "meterdata"))

    if specific_mpid =="707057500057530000" : # The sample
        filename = os.path.join(__location__, specific_file)
        df = pd.read_excel(filename)
        print(df)
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
if __name__ == '__main__':

    api_conn=init_api()
    df=load_assets_from_file("./assets_sample.xlsx")
    for index, row in df.iterrows():
        register_flexible_asset(api_conn, row)
        # Sets hours when KW available
        start_hour=random.randint(6, 10)
        end_hour = random.randint(12, 20)
        crontab = "0 " + str(start_hour) + "-" + str(end_hour) + " * * 1-5"
        register_flex_availability(api_conn, row, crontab)

    meterdata=load_assetmeterdata_from_files(specific_mpid=None)
    for key in meterdata.keys():
        register_meterdata_for_asset(api_conn, key, meterdata[key])
        generate_baseline(key)

    #load_registered_data(api_conn)
