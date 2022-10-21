import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.geolocation.location_api import LocationApi
from energydeskapi.types.location_enum_types import LocationTypeEnum
from energydeskapi.gos.gos_api import GosApi
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])




def get_areas(api_conn):
    # df=LocationApi.get_local_areas(api_conn, LocationTypeEnum.GOs_OFFER_AREA)
    #print("Loc area", df)
    geomdata=LocationApi.generate_default_map(api_conn,map_type="COUNTRY",include_assets=True, zones=['NO4'], country="DNK")
    print(geomdata)
def test_gos(api_conn):
    res=GosApi.get_source_data(api_conn)
    print(res)

if __name__ == '__main__':
    api_conn=init_api()
    get_areas(api_conn)
