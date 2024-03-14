
import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.conversions.elvizlink_api import ElvizLinksApi
from energydeskapi.conversions.energydesklink_api import EnergyDeskinksApi
from energydeskapi.sdk.api_connection import ApiConnection
import environ
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def update_cmpany_mapping(api_conn):
    ElvizLinksApi.upsert_company_mapping(api_conn,"976894677",elviz_company_id=4,
                                         elviz_company_name="E-CO Vannkraft AS")

def load_contracts(api_conn):

    ElvizLinksApi.get_latest_elviz_trades(api_conn,2)

def load_energydesk_trades(api_conn):
    env = environ.Env()
    other_energydesk_token = env.str('OTHER_ENERGYDESK_TOKEN')
    other_energydesk_api_base= env.str('OTHER_ENERGYDESK_URL')
    other_conn=ApiConnection(other_energydesk_api_base)
    other_conn.token=other_energydesk_token
    other_conn.token_type="Token"
    other_conn.base_url=other_energydesk_api_base
    trades=EnergyDeskinksApi.get_latest_energydesk_trades(api_conn, other_conn, 100)

if __name__ == '__main__':
    api_conn=init_api()
    load_energydesk_trades(api_conn)
