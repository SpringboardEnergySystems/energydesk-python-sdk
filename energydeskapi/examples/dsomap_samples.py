import logging
from energydeskapi.sdk.common_utils import key_from_url
from energydeskapi.geolocation.location_api import LocationApi
from energydeskapi.gos.gos_api import GosApi
from energydeskapi.assets.assetgroup_utils import register_new_assetgroup
from energydeskapi.types.asset_enum_types import AssetCategoryEnum
from energydeskapi.assets.assets_api import AssetsApi, AssetSubType, Asset, AssetTechData
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.grid.grid_api import GridApi
import json
import pandas as pd
import geopandas as gpd
import plotly.express as px
from energydeskapi.assets.asset_groups_api import AssetGroupApi, AssetGroup
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])

def load_dso_map(api_conn, name="demodso"):

    dso_res = LocationApi.get_dso_area(api_conn, "demodso")
    data = GridApi.get_capacity_coverage(api_conn)
    feat_coll = dso_res['geojson']
    for x in data:
        if x['grid_loc'] is None:
            continue
        for f in x['grid_loc']['features']:
            if 'TRANSFORMATORSTASJONSKRETS' in f['properties']:
                f['properties']['TRANSFORMATORSTASJONSKRETS'] = str(x['grid_node'])
        feat_coll['features'].extend(x['grid_loc']['features'])
    gdf = gpd.GeoDataFrame.from_features(feat_coll)
    def fix_name(row):
        if str(row['name']) !="nan":
            return row['name']
        return row['label_en']
    gdf['name']=gdf.apply(fix_name, axis=1)
    data = GridApi.get_capacity_coverage(api_conn)
    df=pd.DataFrame(data)
    merged = gdf.set_index('name').join(df.set_index('grid_node'))

    fig = px.choropleth_mapbox(merged, geojson=merged.geometry,         color="capacity",
                               locations=merged.index,center={"lat": dso_res['centroid'][1], "lon": dso_res['centroid'][0]},
                               mapbox_style="carto-positron",zoom=6)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.show()

if __name__ == '__main__':
    api_conn=init_api()
    load_dso_map(api_conn, "demodso")