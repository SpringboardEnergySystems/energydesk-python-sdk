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
    if False:
        for j in range(5):
            gen_orders(api_conn, "856b5c2782a5f001124a423a5418d2e7bba1304b", 65, "BUY")
            gen_orders(api_conn, "74cdfbb1bbcf8856112655f79d41867435c6085d", 65, "BUY")
            gen_orders(api_conn, "7e63ca032791c213ce0789e0bf64ab131e9658d0", 75, "SELL")
            gen_orders(api_conn, "9b50f5e43795d9c6e45bb08fd2a4a24ebcff7e49", 75, "SELL")
    for j in range(3):
        gen_orders(api_conn, "a6e685b5062ad1fbfce422fe5d703bf3e52ba2cb", 66, "SELL")

