
import logging
from energydeskapi.portfolios.tradingbooks_api import TradingBooksApi
from energydeskapi.sdk.common_utils import init_api
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def query_trading_books(api_conn):
    df=TradingBooksApi.get_tradingbooks_df(api_conn)
    print(df[['pk','description']])


if __name__ == '__main__':
    api_conn=init_api()
    query_trading_books(api_conn)
