import sys
import json
from random import randrange
import requests
import logging
import random
from datetime import datetime
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.lems.lems_api import LemsApi
from energydeskapi.types.clearing_enum_types import ClearingReportTypeEnum
import pandas as pd
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])



def gen_orders(api_conn, token, baseprice, ordertype):
    api_conn.set_token(token, "Token")
    df = LemsApi.get_traded_products(api_conn)
    for index, row in df.iterrows():
        if row['area']=="NO1" or row['area']=="NO2" or row['area']=="NO5":
            useprice=baseprice
        else:
            useprice=baseprice/2
        qty = 5 + randrange(15)
        price = useprice + random.uniform(1.5, 5.5)
        price = round(price, 1)
        #print("Adding ", row['ticker'], price, qty)
        LemsApi.add_order(api_conn, row['ticker'], price, qty, ordertype)
def get_ticker_data(api_conn):
    df=LemsApi.get_traded_products(api_conn)
    #print(df)
    ticker = df["ticker"].values[2]
    LemsApi.add_order(api_conn, ticker, 100, 5, "BUY")
    LemsApi.add_order(api_conn, ticker, 93, 2, "SELL")
    LemsApi.add_order(api_conn, ticker, 193, 7, "SELL")
    
    df=LemsApi.query_active_orders(api_conn, ticker)
    order_id = df["order_id"].values[0]
    print(df)

    df=LemsApi.remove_order(api_conn, ticker, order_id)
    print(df)
    
    df=LemsApi.query_own_orders(api_conn, ticker)
    print(df)

    df=LemsApi.get_ticker_data(api_conn)
    print(df)
if __name__ == '__main__':

    api_conn=init_api()
    random.seed(datetime.now())
    for j in range(5):
        gen_orders(api_conn, "241a85c905e36c0316d3d58be9cae9d3d5bc7d5a", 65, "BUY")
        gen_orders(api_conn, "2ba840008a1276d953bb708c0ecd8bf8251355ac", 65, "BUY")
        gen_orders(api_conn, "03cace913e56d29abc02ec9ebec250913b9b7ee2", 75, "SELL")
        gen_orders(api_conn, "28bffd50de26b4c9649402ab4c6dc48ca1e391ac", 75, "SELL")

    gen_orders(api_conn, "23f9dc04336c4a1d62dcd4f37585c4e1d16d58ac", 66, "SELL")

