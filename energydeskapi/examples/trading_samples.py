import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.lems.lems_api import LemsApi
import pandas as pd
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


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
    df = LemsApi.get_traded_products(api_conn)
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


def add_buy_order_on_nearest_products(api_conn,  price, currency, quantity_mw):
    df_products = get_available_products(api_conn)
    # For simplicity and test, pick the first product
    sample_ticker = df_products["ticker"].values[0]
    success, json_res, status_code, error_msg = LemsApi.add_order(
        api_conn, sample_ticker, price, currency, quantity_mw, "BUY", "FOK")
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
    df_all_trades = LemsApi.query_own_trades(api_conn)
    print(df_all_trades)
    return df_all_trades


if __name__ == '__main__':
    api_conn = init_api()
    add_buy_order_on_nearest_products(api_conn, 1900, "NOK", quantity_mw=3)  # 0.5 MW in sample
    # remove_all_active_orders(api_conn)
    get_own_orders_total(api_conn)
    get_own_trades_total(api_conn)
    # get_live_orderbook(api_conn)
