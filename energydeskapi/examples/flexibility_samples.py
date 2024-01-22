import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.energydesk.general_api import GeneralApi
from energydeskapi.flexibility.dso_api import DsoApi
from energydeskapi.flexibility.flexibility_api import FlexibilityApi
import pendulum
import json
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])





def register_flexible_asset(api_conn):
    outdata=FlexibilityApi.register_flexible_asset(api_conn, external_id="123asset",
                                                   description="Fryselager",
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


if __name__ == '__main__':

    api_conn=init_api()
    register_flexible_asset(api_conn)
