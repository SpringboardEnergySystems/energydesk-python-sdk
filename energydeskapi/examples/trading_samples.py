import random
from datetime import datetime, timedelta
import logging
from random import randrange
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.bilateral.bilateral_api import BilateralApi
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
def get_own_active_orders(api_conn, ticker=None):
    df = LemsApi.query_own_orders(api_conn, True, ticker)
    print(df)
    return df

# Returns an anonymous view of orders in local market


def get_live_orderbook(api_conn):
    df = LemsApi.query_active_anonymous_orders(api_conn)
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
        df_orders = get_own_active_orders(api_conn, row['ticker'])
        print("Own orders (incl filled) on ", row['ticker'])
        print(df_orders)
        for index2, row2 in df_orders.iterrows():
            if row2['order_status'] != 'ACTIVE':
                continue
            LemsApi.remove_order(api_conn, row['ticker'], row2['order_id'])

# Example of adding a buy order to match orders in the live orderbook


def add_buy_order_on_products(api_conn,  price, currency,ticker, quantity_mw, extern_comp_regnr):

    extern_comp_name=get_comp_name_from_regnumber(extern_comp_regnr)
    print(extern_comp_regnr, extern_comp_name)

    success, json_res, status_code, error_msg = LemsApi.add_buyer_order(
        api_conn, ticker, price, currency, quantity_mw, "FOK", expiry=None, extern_comp_reg= extern_comp_regnr,
        extern_comp_name=extern_comp_name )
    if success:
        print(json_res)
    else:
        print(error_msg)
    # Should see filled orders after previous operatgion
    df_own_orders = LemsApi.query_own_orders(api_conn)
    print(df_own_orders)


def add_sell_order_on_products(api_conn,  price, currency,product_idx, quantity_mw, is_pending=False):
    df_products = get_available_products(api_conn)
    sample_ticker = df_products["ticker"].values[product_idx]
    expiry = (datetime.today() + timedelta(days=10)).strftime("%Y-%m-%d")
    status="ACTIVE" if not is_pending else "PENDING"
    LemsApi.add_order(api_conn, sample_ticker,price,currency, quantity_mw, "SELL", "NORMAL", expiry, status)
    print("Order added. Now query res")
    df_own_orders = LemsApi.query_own_orders(api_conn)
    print(df_own_orders)

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




def get_contract_doc(api_conn, ticker, quantity, deal_id):
    r=BilateralApi.load_profiled_volume(api_conn, ticker, float(quantity))
    print(r)
    tex_content = LemsApi.get_contract_doc(api_conn,deal_id)
    print(tex_content)
    f=open("./sample.tex","w")
    f.write(tex_content['tex_file'])
    f.close()
    #pdf = LatexApi.download_pdf_attachment(api_conn, tex_content)
    #print(pdf)

def get_own_orders_total(api_conn):
    df_all_orders = LemsApi.query_own_orders(api_conn)
    print(df_all_orders)
    return df_all_orders


def get_own_trades_total(api_conn):
    df_all_trades = LemsApi.get_own_trades_df(api_conn)
    print(df_all_trades)
    return df_all_trades

def get_contract_doc_lastdeal(api_conn):
    deals=get_own_trades_total(api_conn)
    if len(deals.index)==0:
        print("No deals")
        return None
    deal=deals.iloc[len(deals.index)-1]
    print(deal)
    get_contract_doc(api_conn,deal['ticker'],deal['quantity'], deal['deal_id'])

if __name__ == '__main__':

    api_conn = init_api()
    get_contract_doc_lastdeal(api_conn)



