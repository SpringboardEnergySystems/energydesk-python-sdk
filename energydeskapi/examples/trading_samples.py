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



# Random order generator
def gen_orders(api_conn, baseprice, ordertype, token=None):
    random.seed(datetime.now())
    if token is not None:
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
        LemsApi.add_order(api_conn, row['ticker'], price,"EUR", qty, ordertype)



# Returns an anonymous view of orders in local market
def get_own_orders(api_conn, ticker):
    df=LemsApi.get_own_orders(api_conn, ticker)
    print(df)
    return df


# Returns an anonymous view of orders in local market
def get_live_orderbook(api_conn):
    df = LemsApi.query_active_orders(api_conn)
    print(df)
    return df

# Returns an anonymous view of orders in local market
def get_available_products(api_conn):
    df = LemsApi.get_traded_products(api_conn)
    print(df)
    return df

# Example of adding a buy order to match orders in the live orderbook
def add_buy_order_on_nearest_products(api_conn,  price,currency, quantity_mw):
    df_products=get_available_products(api_conn)
    sample_ticker = df_products["ticker"].values[0]  #For simplicity and test, pick the first product
    success, json_res, status_code, error_msg = LemsApi.add_order(api_conn,sample_ticker,price, currency, quantity_mw, "BUY")
    if success:
        print(json_res)
    # Should see filled orders after previous operatgion
    get_own_orders(api_conn, sample_ticker)

    order_id=""  #If picking one of own active orders (none filled) this can be cancelled by following
    df = LemsApi.remove_order(api_conn, sample_ticker, order_id)

def add_random_sell_products(api_conn):
    # Ransom prices around a price
    for j in range(10):
        gen_orders(api_conn,  73, "SELL", None)

if __name__ == '__main__':
    api_conn=init_api()
    add_buy_order_on_nearest_products(api_conn, 900, "NOK", quantity_mw=0.5)  # 0.5 MW in sample

