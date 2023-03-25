import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.moneymarkets.moneymarkets_api import MoneyMarketsApi
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])




def get_moneymarket_data(api_conn):
    #MoneyMarketsApi
    pass

def fetch_fxspot(api_conn):
    currency_date, df = MoneyMarketsApi.get_fxspot(api_conn, {"days_back":53, "currency_date":"2023-03-04"})
    print("Got FX spot rates for date ", currency_date)
    print(df)

def fetch_fxtenors(api_conn):
    currency_date, df =  MoneyMarketsApi.get_fxtenors(api_conn, {"days_back":53, "currency_date":"2023-03-09"})
    print(df)

def fetch_yieldcurves(api_conn):
    param = {"currency_date":"2023-03-22"}
    currency_date, df =  MoneyMarketsApi.get_fwd_curves(api_conn, param)
    print(df)
    #df2 = MoneyMarketsApi.get_fwdrates(api_conn, param)
    #print(df2)

if __name__ == '__main__':

    api_conn=init_api()
    # get_moneymarket_data(api_conn)
    #fetch_fxspot(api_conn)
    fetch_yieldcurves(api_conn)
    #fetch_fxtenors(api_conn)
