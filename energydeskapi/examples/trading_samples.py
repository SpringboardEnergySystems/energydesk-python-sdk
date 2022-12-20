import random
from datetime import datetime
import logging
from random import randrange
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.lems.lems_api import LemsApi
from energydeskapi.pdfgenerator.latex_api import LatexApi
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


def get_contract_doc(api_conn):
    tex_content = LemsApi.get_contract_doc(api_conn, "a61f30fa-1385-4c28-9347-7c64fd131951")
    print(tex_content)
    f=open("./sample.tex","w")
    f.write(tex_content['tex_file'])
    f.close()
    #pdf = LatexApi.download_pdf_attachment(api_conn, textfile)
    #print(pdf)

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
    volte1="bb98d5f7e9387118ae325b2e5b71686e2c1ac150"
    voltetest2 = "a62b59e7a46bf3bbd7d93c5cf5314cadf239fdec"
    ent1="555a94fbb9d09e987ee2762a027fae209a333384"
    enttest2 = "d503d740ea0ff61290297ecbfb9e2279c0588551"
    api_conn = init_api()

    #get_contract_doc(api_conn)
    #sys.exit(0)
    #get_own_trades_total(api_conn)
    list1 = ['920369820','925891576','913320506', '927856026', '927856026', '985274762']
    list2 =['970980105','970234934','820431472','820431472','979437218']
    #Samples of 2 users from different companies
    for comp in [(volte1, list1), (ent1,list2)]:
        api_conn.set_token(comp[0], "Token")
        v = random.uniform(0.1, 0.5)
        externals=comp[1]
        for i in range(25):
            product_idx=randrange(4,24)
            extern_customer_idx = randrange(len(externals))
            add_buy_order_on_products(api_conn, 1900, "NOK",product_idx, quantity_mw=v, extern_comp_regnr=externals[extern_customer_idx])  # 0.5 MW in sample
    # remove_all_active_orders(api_conn)
    #get_own_orders_total(api_conn)
    #get_own_trades_total(api_conn)
    # get_live_orderbook(api_conn)
