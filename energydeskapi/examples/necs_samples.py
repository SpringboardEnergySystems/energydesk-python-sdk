import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.necs.necs_api import NecsApi

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])

def fetch_necs_certificates(api_conn):
    result = NecsApi.get_necs_certificates(api_conn)
    print(result)

def fetch_necs_certificate_by_key(api_conn):
    pk = 2
    result = NecsApi.get_necs_certificate_by_key(api_conn, pk)
    print(result)


if __name__ == '__main__':
    api_conn = init_api()
    fetch_necs_certificates(api_conn)
    fetch_necs_certificate_by_key(api_conn)
