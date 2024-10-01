import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.energydesk.general_api import GeneralApi
from energydeskapi.flexibility.dso_api import DsoApi
from energydeskapi.types.common_enum_types import PeriodResolutionEnum
from energydeskapi.types.flexibility_enum_types import RegulatingDirectionEnums, ReservesTypeEnums, ReservesCategoryEnum
from energydeskapi.sdk.datetime_utils import conv_from_pendulum
from energydeskapi.flexibility.flexibility_api import FlexibilityApi, ExternalMarketAsset
from energydeskapi.grid.grid_api import GridApi
import pendulum
import json
import pandas as pd
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])





def register_flexible_asset(api_conn):
    outdata=FlexibilityApi.register_flexible_asset(api_conn, extern_asset_id="67Varanger",
                                                   description="67Varanger",
                                                   meter_id="7055122312321",
                                                   sub_meter_id="1231",
                                                   address="Ikke gyldig 12",
                                                   city="Oslo",
                                                   latitude=10.778198726739516,
                                                   longitude=59.73425547038753,
                                                   asset_category="CONSUMPTION",
                                                   asset_type="Ventilasjon",
                                                   asset_owner_regnumber="876944642",
                                                   asset_manager_regnumber="876944642",
                                                   dso_regnumber="980489698",
                                                   brp_company_regnumber="876944642",
                                                   callback_url="http://127.0.0.1:8090/callback"
                                           )
    print(outdata)





def register_flex_availability(api_conn):
    t1="2024-02-01 00:00:00+02:00"
    t2="2024-03-01 00:00:00+02:00"
    crontab="0 11-13 * * 1-5"   # 11 12 and 13 monday-friday

    outdata=FlexibilityApi.register_asset_availability(api_conn,extern_asset_id="67Varanger",
                                               period_from=t1, period_until=t2,
                                               crontab=crontab, kw_available=200)
    print(outdata)

def check_schedule(api_conn):
    t1="2024-02-01"
    t2="2024-02-03"
    outdata=FlexibilityApi.get_availability_schedule(api_conn,extern_asset_id="67Varanger",
                                                     period_from=t1,period_until=t2)
    print(outdata)


def load_gridnode_polygons(api_conn, df):
    gridnodes = list(df['gnode_id'].unique())
    print(gridnodes)
    res=FlexibilityApi.load_grid_node_polygons(api_conn, gridnodes)
    print(res)
def find_flexibility_potential(api_conn):
    payload={}
    payload['flexible_assets']=[]
    payload['flexible_assets'].append({'address':'Tiriltunga, Oslo','kw':200 })
    payload['flexible_assets'].append({'address': 'Holmlia Senter vei 16, Oslo', 'kw': 200})
    payload['flexible_assets'].append({'address': 'Nedre Prinsdals vei 79, 1263 Oslo', 'kw': 100})
    success, returned_data, status_code, error_msg = FlexibilityApi.find_flexibility_potential(api_conn, payload)
    df = pd.DataFrame(returned_data)
    return df
def load_lonflex_agreements(api_conn):
    returned_data = FlexibilityApi.load_lonflex_agreements(api_conn)
    df = pd.DataFrame(returned_data)
    def conv_datetime(row):
        t=row['period_to']
        t=pendulum.parse(t)
        return conv_from_pendulum(t)
    df['period_to'] = df.apply(conv_datetime, axis=1)
    df=df.loc[df['period_to']>conv_from_pendulum(pendulum.today())]
    df['total_availability_payment']=df['flexhours']*df['availability_price']
    df=df.sort_values(by=['total_availability_payment', 'activation_price'],ascending=False)
    print(df)

def load_registered_data(api_conn):
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

def load_capacity_coverage(api_conn):
    data=GridApi.get_capacity_coverage(api_conn)
    print(len(data))

def load_reserves_prices(api_conn):
    data=FlexibilityApi.get_reserves_prices(api_conn, {'regulating_direction__code': RegulatingDirectionEnums.UP.name,'reserves_type__code':ReservesTypeEnums.mFRR.name})
    df=pd.DataFrame(data)
    print(df)
if __name__ == '__main__':

    api_conn=init_api()
    register_flexible_asset(api_conn)
    register_flex_availability(api_conn)
    #df=find_flexibility_potential(api_conn)
    #load_reserves_prices(api_conn)
