import random
from datetime import datetime
import logging
from random import randrange
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.lems.lems_api import LemsApi
import pandas as pd
import requests
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])

regmap={}
def get_comp_name_from_regnumber(regnumber):
    if regnumber in regmap:
        return regmap[regnumber]
    url = "https://data.brreg.no/enhetsregisteret/api/enheter/" + regnumber

    result = requests.get(url)
    if result.status_code>=400:
        return ""
    try:
        name=result.json()['navn']
        regmap[regnumber]=name
        return name
    except:
        pass
    return ""
# Returns an anonymous view of orders in local market
def get_own_orders(api_conn, ticker):
    df = LemsApi.query_own_orders(api_conn, ticker)
    print(df)
    return df

# Returns an anonymous view of orders in local market


def get_live_orderbook(api_conn):
    df = LemsApi.query_active_orders(api_conn)
    print(df)
    return df


# Returns an anonymous view of orders in local market
def get_available_products(api_conn):
    df = LemsApi.get_traded_products_df(api_conn)
    print(df)
    return df


def remove_all_active_orders(api_conn):
    df_products = get_available_products(api_conn)
    for index, row in df_products.iterrows():
        df_orders = get_own_orders(api_conn, row['ticker'])
        print("Own orders (incl filled) on ", row['ticker'])
        print(df_orders)
        for index2, row2 in df_orders.iterrows():
            if row2['order_status'] != 'ACTIVE':
                continue
            LemsApi.remove_order(api_conn, row['ticker'], row2['order_id'])

# Example of adding a buy order to match orders in the live orderbook


def add_buy_order_on_products(api_conn,  price, currency,product_idx, quantity_mw, extern_comp_regnr):

    extern_comp_name=get_comp_name_from_regnumber(extern_comp_regnr)
    print(extern_comp_regnr, extern_comp_name)
    df_products = get_available_products(api_conn)
    # For simplicity and test, pick the first product
    sample_ticker = df_products["ticker"].values[product_idx]
    success, json_res, status_code, error_msg = LemsApi.add_buyer_order(
        api_conn, sample_ticker, price, currency, quantity_mw, "FOK", expiry=None, extern_comp_reg= extern_comp_regnr,
        extern_comp_name=extern_comp_name )
    if success:
        print(json_res)
    else:
        print(error_msg)
    # Should see filled orders after previous operatgion
    df = get_own_orders(api_conn, sample_ticker)
    print(df)


# Example of retrieving own orders for set of products
def get_own_orders_per_product(api_conn):
    df_all_orders = pd.DataFrame()
    # PS If looping through *all* products, this is the same as querying (once) without specifying the ticker code of the product
    df_products = get_available_products(api_conn)
    for index, row in df_products.iterrows():
        df_orders = LemsApi.query_own_orders(api_conn, row['ticker'])
        if len(df_orders) > 0:
            print("Found own orders on ", row['ticker'])
            df_all_orders = df_all_orders.append(df_orders)
    print(df_all_orders)
    return df_all_orders

# Example of retrieving own orders regardless of product


def get_own_orders_total(api_conn):
    df_all_orders = LemsApi.query_own_orders(api_conn)
    print(df_all_orders)
    return df_all_orders

# Example of retrieving own orders regardless of product


def get_own_trades_total(api_conn):
    df_all_trades = LemsApi.get_own_trades_df(api_conn)
    print(df_all_trades)
    return df_all_trades
import sys

if __name__ == '__main__':
    random.seed(datetime.now())
    api_conn = init_api()
    #get_own_trades_total(api_conn)
    list1 = ['920369820','925891576','913320506', '927856026', '927856026', '985274762']
    list2 =['970980105','970234934','820431472','820431472','979437218']
    #Samples of 2 users from different companies
    for comp in [("82a85b9cbdd30be50a343a475e885905bf778494", list1), ("af0ac457fa7315ea96291c9e438586915bffad5c",list2)]:
        api_conn.set_token(comp[0], "Token")
        v = random.uniform(0.1, 0.5)
        externals=comp[1]
        for i in range(25):
            product_idx=randrange(5)
            extern_customer_idx = randrange(len(externals))
            add_buy_order_on_products(api_conn, 1900, "NOK",product_idx, quantity_mw=v, extern_comp_regnr=externals[extern_customer_idx])  # 0.5 MW in sample
    # remove_all_active_orders(api_conn)
    #get_own_orders_total(api_conn)
    #get_own_trades_total(api_conn)
    # get_live_orderbook(api_conn)
