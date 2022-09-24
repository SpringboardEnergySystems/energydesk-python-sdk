import sys

import requests
import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.conversions.elvizlink_api import ElvizLinksApi

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def update_cmpany_mapping(api_conn):
    ElvizLinksApi.upsert_company_mapping(api_conn,"976894677",elviz_company_id=4,
                                         elviz_company_name="E-CO Vannkraft AS")

if __name__ == '__main__':
    api_conn=init_api()
    update_cmpany_mapping(api_conn)
