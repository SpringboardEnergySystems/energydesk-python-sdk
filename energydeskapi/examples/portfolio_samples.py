
import logging
import json
from energydeskapi.portfolios.portfoliotree_api import PortfolioTreeApi
from energydeskapi.sdk.common_utils import init_api
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def query_portfolios(api_conn):
    js=PortfolioTreeApi.get_portfolio_tree(api_conn)
    print(json.dumps(js, indent=4))
    js=PortfolioTreeApi.get_portfolio_flat_tree(api_conn)
    print(json.dumps(js, indent=4))

if __name__ == '__main__':
    api_conn=init_api()
    query_portfolios(api_conn)
