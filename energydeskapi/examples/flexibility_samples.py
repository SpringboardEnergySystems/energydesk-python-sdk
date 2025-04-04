import geojson
import geopandas as gpd
import matplotlib  # pip install matplotlib
import plotly.express as px
import plotly.graph_objects as go
from matplotlib.pyplot import *
from shapely.geometry import shape

matplotlib.use('agg')
matplotlib.style.use('ggplot')
import logging
from django.urls import reverse
from django.shortcuts import render
from bokeh.resources import INLINE
import requests
import pendulum
import json
from energydeskapi.types.flexibility_enum_types import RegulationTypeEnums
from django.shortcuts import redirect

import pandas as pd
from energydeskapi.flexibility.flexibility_api import FlexibilityApi, AssetScheduledRegulation
from energydeskapi.assets.asset_groups_api import AssetGroupApi, AssetGroup
from energydeskapi.assets.assets_api import AssetsApi
import json
from energydeskapi.sdk.pandas_utils import make_empty_timeseries_df
from energydeskapi.sdk.money_utils import FormattedMoney, CurrencyCode
import pandas as pd
from energydeskapi.contracts.contracts_api import ContractsApi
import pendulum
from energydeskapi.customers.customers_api import CustomersApi
from energydeskapi.customers.users_api import UsersApi
from energydeskapi.flexibility.capacity_contract_utils import generate_default_activation_contract
from energydeskapi.flexibility.flexibility_api import ExternalMarketAsset
from energydeskapi.flexibility.flexibility_api import FlexibilityApi
from energydeskapi.grid.grid_api import GridApi
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.sdk.datetime_utils import conv_from_pendulum
from energydeskapi.types.flexibility_enum_types import RegulatingDirectionEnums
from energydeskapi.types.flexibility_enum_types import ReservesCategoryEnum
from energydeskapi.flexibility.flexibility_qa_api import FlexibilityQaApi
from energydeskapi.flexibility.flexibility_portfolios_api import FlexibilityPortfolioApi, FlexPortfolio, FlexPortfolioTrade
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])



def register_flex_contract(api_conn):
    contract=generate_default_activation_contract(api_conn)
    print(contract)
    comp=CustomersApi.get_company_from_registry_number(api_conn, "980489698")
    print(comp)
    up=UsersApi.get_user_profile(api_conn)
    print(up)
    today = pendulum.today("Europe/Oslo")
    next=pendulum.tomorrow("Europe/Oslo")
    next2=next.add(hours=1)
    contract.counterpart = comp['pk']
    #contract.external_contract_id = contract_type + "_" + str(contracted_asset['meter_id'])
    contract.trader = up['pk']
    contract.quantity = 5
    contract.contract_profile=None
    contract.contract_price = FormattedMoney(10, CurrencyCode.NOK)
    contract.trade_datetime = today
    contract.trade_date = today
    contract.trading_book = 4
    #contract.counterpart = counterpart_pk


    contract.commodity_delivery_from = next
    contract.commodity_delivery_until = next2
    #contract.contract_sub_type = contract_type
    success, returned_data, status_code, error_msg = ContractsApi.upsert_contract(api_conn, contract)


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
    t1="2025-03-13 12:00:00+01:00"
    t2="2025-03-14 00:00:00+01:00"
    df = make_empty_timeseries_df(t1, t2, "H", "Europe/Oslo")
    df=df.tz_convert("Europe/Oslo")
    df['timestamp']=df.index
    df['value'] = 100
    df['date'] = df.index.date
    print(df)
    print(json.loads(df.to_json(orient='records')))

    prof={'absolute_profile':json.loads(df.to_json(orient='records', date_format='iso'))}
    for a in prof['absolute_profile']:
        a['date']=a['date'][:10]
    outdata=FlexibilityApi.register_asset_availability(api_conn,asset_id=None, extern_asset_id="Skur 88",
                                               period_from=t1, period_until=t2,active_profile=None,profile_changerequest=prof,kw_available=None,avgcost_per_unit=0)


    print(outdata)

def check_schedule(api_conn):
    t1="2024-02-01"
    t2="2024-02-03"
    outdata=FlexibilityApi.get_availability_schedule(api_conn,extern_asset_id="Kalnes VGS",
                                                     period_from=t1,period_until=t2)
    print(outdata)


def create_dispatch(api_conn):
    asset=681
    regulation =600

    d1=pendulum.tomorrow(tz="Europe/Oslo").in_timezone("UTC")
    d2=d1.add(hours=1)

    rec=AssetsApi.get_asset_by_key(api_conn, asset)
    param = {}
    if rec is not None:
        print(rec)
        param['asset__id']=asset
    print(param)
    outdata=FlexibilityApi.get_flexible_assets_embedded(api_conn, param)
    print(outdata['results'])
    print(outdata['results'])
    extern_asset_id = outdata['results'][0]['asset']['extern_asset_id']
    asr=AssetScheduledRegulation(outdata['results'][0]['pk'], float(regulation), d1 , d2, extern_asset_id)
    asr.regulation_type = RegulationTypeEnums.REGULATE_UP.value

    FlexibilityApi.upsert_scheduled_regulation(api_conn, asr)


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


def plot_price(type_name, df):
    df['time']=df.index
    fig = go.Figure()  # generating a figure that will be updated in the following lines
    fig.add_trace(go.Scatter(x=df.time, y=df.price,
                                        mode='lines',  # you can also use "lines+markers", or just "markers"
                                        name='Capacity Price on ' + str(type_name)))
    fig.layout.template = 'plotly_white'
    fig.layout.height = 500
    fig.update_layout(margin=dict(t=50, b=50, l=25, r=25))  # this will help you optimize the chart space
    fig.update_layout(
        #     title='Global Portfolio Value (USD $)',
        xaxis_tickfont_size=12,
        yaxis=dict(
            title='Price EUR/MWh',
            titlefont_size=14,
            tickfont_size=12,
        ))
    return fig

def load_reserves_prices(api_conn):
    data=FlexibilityApi.get_reserves_prices(api_conn,
                                            {'regulating_direction__code': RegulatingDirectionEnums.UP.name,
                                             'reserves_category__code':ReservesCategoryEnum.CAPACITY.name})
    df=pd.DataFrame(data)

    df['timestamp']=pd.to_datetime(df["timestamp"])
    df=df.loc[df.timestamp>pendulum.today(tz="UTC").add(days=-5)]
    df3=df.groupby(["reserves_type",'timestamp']).agg({'area':'max','regulating_direction':'max','reserves_category':'max','price':'sum'})
    print(df3)
    for tp, new_df in df3.groupby(level=0):
        plot_price(tp, new_df.droplevel(0))
def get_flexibility_products(api_conn):
    data=FlexibilityApi.get_flexibility_products(api_conn)
    df=pd.DataFrame(data)
    print(df)

def test_trade(api_conn):
    #FlexibilityPortfolioApi, FlexPortfolio, FlexPortfolioTrade
    reg_direction = FlexibilityApi.get_regulation_direction_url(api_conn,
                                                                RegulatingDirectionEnums.UP)
    res_category = FlexibilityApi.get_reserves_categories_url(api_conn,
                                                              ReservesCategoryEnum.ACTIVATION)
    fport=FlexPortfolio(0,"Porto","porto","porto2","-", ['1'])
    FlexibilityPortfolioApi.upsert_flexible_portfolio(api_conn,fport)
    contr_url=ContractsApi.get_contract_url(api_conn, 674)
    port_url=FlexibilityPortfolioApi.get_flexible_portfolio_url(api_conn, 1)
    reservs_url=ReservesCategoryEnum.ACTIVATION.value
    tr=FlexPortfolioTrade(0,contr_url,port_url,reg_direction,res_category,"{}")
    print(tr.json)
    FlexibilityPortfolioApi.upsert_flexible_portfolio_trade(api_conn,tr)

def get_qa_data(api_conn):
    # data=FlexibilityQaApi.get_flexassets(api_conn, {'page_size': 900})
    # df=pd.DataFrame(data['results'])
    # print(df.columns)
    # df=df[['asset_id', 'registration_date','description', 'grid_node', 'fsp', 'asset_type','installed_effect']]
    #
    # df['installed_effect']=df['installed_effect'].fillna(0)
    # df['installed_effect'] = df['installed_effect'].astype('Float64')
    # print(df)
    # d2f=df.groupby(['grid_node','fsp']).agg({'installed_effect':'sum'})
    # #print(d2f)
    # #print(df)
    # return

    contracts=FlexibilityQaApi.get_longflexcontracts_embedded(api_conn, {'page_size': 900})
    energy_profile={}
    contract_summary=[]
    df_tot=None
    for c in contracts['results']:
        cs={}
        cs['trade_datetime']=c['trade_datetime']
        cs['participant'] = c['participant_name']
        cs['period_from'] = c['period_from']
        cs['period_until'] = c['period_until']
        cs['price'] = c['price_amount']
        cs['quantity'] = c['quantity']
        cs['grid_nodee'] = c['grid_node_name']
        prof=json.loads(c['profile'])
        dfprof=pd.DataFrame(prof)
        dfprof.index=dfprof['hour']
        dfprof.index = pd.to_datetime(dfprof.index)
        dfprof['fsp']=c['participant_name']
        dfprof['grid'] = c['grid_node_name']
        dfprof2=dfprof.resample('MS').agg({'effect':'sum', 'grid':'first','fsp':'first'})
        if df_tot is None:
            df_tot=dfprof2
        else:
            df_tot=pd.concat([df_tot,dfprof2])
        contract_summary.append(cs)
    df=pd.DataFrame(contract_summary)

    print(df)
    print(df.columns)
    print(df_tot)
    df_tot.index.names = ['index']
    df_tot['hour']=df_tot.index
    df_tot2=df_tot.groupby(['hour', 'fsp']).agg({'effect':'sum'})

    print(df_tot2)
    df_tot2 = df_tot.groupby(['hour', 'grid']).agg({'effect': 'sum'})
    print(df_tot2)
    #df_tot2 = df.open.resample('W').mean()
    #print(df_tot2)



if __name__ == '__main__':
    #pd.set_option('display.max_rows', None)
    api_conn=init_api()
    #register_flexible_asset(api_conn)
    #get_qa_data(api_conn)
    create_dispatch(api_conn)
    #check_schedule(api_conn)

    #load_reserves_prices(api_conn)
