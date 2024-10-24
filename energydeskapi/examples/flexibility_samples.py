import json
import logging

import geojson
import geopandas as gpd
import pandas as pd
import pendulum
import logging
import json
from shapely.geometry import shape
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import plotly.express as px

import pandas as pd     # pip install pandas

import numpy as np
from matplotlib.pyplot import *
import matplotlib

import matplotlib      # pip install matplotlib
matplotlib.use('agg')
matplotlib.style.use('ggplot')
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import pendulum
from energydeskapi.flexibility.flexibility_api import ExternalMarketAsset
from energydeskapi.flexibility.flexibility_api import FlexibilityApi
from energydeskapi.grid.grid_api import GridApi
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.sdk.datetime_utils import conv_from_pendulum
from energydeskapi.types.flexibility_enum_types import RegulatingDirectionEnums
from energydeskapi.types.flexibility_enum_types import ReservesTypeEnums

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


def draw_map(node_polygons, valuemap):
    feat_coll = {'type': 'FeatureCollection', 'features': []}
    for x in node_polygons['grid_nodes']:
        x['polygon']['features'][0]['id']=x['grid_node_id']
        x['polygon']['features'][0]['type'] = "Feature"
        x['polygon']['features'][0]['properties'] = {'name':x['grid_node_name'],
                                                     'value': valuemap[x['grid_node_id']],
                                                     'id':x['grid_node_id']}
        print(x['polygon']['features'][0]['properties'])
        feat_coll['features'].extend(x['polygon']['features'])
    df = gpd.GeoDataFrame.from_features(feat_coll)
    df=df.fillna(0)
    df['type']=0

    geojs=df.to_json()
    #print(feat_coll['features'])
    bounds=shape(feat_coll['features'][0]['geometry']).bounds
    print("bounds ", bounds)
    center = shape(feat_coll['features'][0]['geometry']).centroid
    centroid = json.loads(geojson.dumps(center))['coordinates']
    df = gpd.GeoDataFrame.from_features(json.loads(geojs))
    df['id'] = df.index
    df = df.dropna(subset=['geometry'])
    print(df)

    #zoom, box_center=get_plotting_zoom_level_and_center_coordinates_from_lonlat_tuples(np.array(lons), np.array(lats))
    zoom= 7
    colorscale = [ "rgb(33, 74, 12)","rgb(67, 136, 33)", "rgb(94, 179, 39)","rgb(210, 231, 154)","rgb(255, 51, 51)"]
    fig = px.choropleth_mapbox(df, geojson=df.geometry, color="value",
                               color_continuous_scale=colorscale, opacity=0.5,
                               featureidkey='id',
                               hover_data=["name", "value"],zoom=zoom,
                               locations="id", center={"lat": centroid[1], "lon": centroid[0]},
                               mapbox_style="carto-positron")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(clickmode='event+select')
    return fig

def load_gridnode_polygons(api_conn, df):
    gridnodes = list(df['gnode_id'].unique())
    valuemap={}
    for index, row in df.iterrows():
        if row['gnode_id'] not in valuemap:
            valuemap[row['gnode_id']]=0
        valuemap[row['gnode_id']]+=row['total_availability_payment']
    res=FlexibilityApi.load_grid_node_polygons(api_conn, gridnodes)
    fig=draw_map(res, valuemap)
    fig.show()
    #for r in res['grid_nodes']:
    #    print(r.keys())
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
    df=df.loc[df['period_to']>conv_from_pendulum(pendulum.parse('2024-09-30'))]
    df['total_availability_payment']=df['flexhours']*df['availability_price']
    df=df.sort_values(by=['total_availability_payment', 'activation_price'],ascending=False)
    print(df.columns)

    def fix_datetime(row):
        t1=row['period_from']
        t2 = row['period_to']
        t1=str(t1)[0:13] + ":00:00"
        t2 = str(t2)[0:13] + ":00:00"
        row['period_from']=t1
        row['period_to'] = t2
        return row

    df=df.apply(fix_datetime, axis=1)
    print(df)

    #df = df.drop(columns=['period_from', 'period_until', 'date'])
    df.to_excel("./longflex_value.xlsx")
    load_gridnode_polygons(api_conn, df)
    #print(df)

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
    #pd.set_option('display.max_rows', None)
    api_conn=init_api()
    #register_flexible_asset(api_conn)
    #register_flex_availability(api_conn)
    df=load_lonflex_agreements(api_conn)
    print(df)
    #load_reserves_prices(api_conn)
