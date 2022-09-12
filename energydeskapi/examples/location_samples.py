import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.geolocation.location_api import LocationApi

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])




def get_areas(api_conn):
    df=LocationApi.get_main_production_area(api_conn)
    print("Main area", df)



if __name__ == '__main__':

    api_conn=init_api()
    get_areas(api_conn)
