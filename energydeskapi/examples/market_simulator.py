
import logging
import json
import time
import random
from energydeskapi.events.mqtt_events_api import MqttClient
import environ
from datetime import datetime
import logging
from random import randrange
import pandas as pd
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.marketdata.derivatives_api import DerivativesApi
from energydeskapi.marketdata.markets_api import MarketsApi
from energydeskapi.marketdata.spotprices_api import SpotPricesApi
from energydeskapi.marketdata.products_api import ProductsApi
from energydeskapi.types.market_enum_types import MarketEnum, CommodityTypeEnum, InstrumentTypeEnum
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])

def generate_send_marketdata(mqttcli, df,  ticker_idx, ticker):
    area = "SYS" if ticker[:3] == "ENO" else ticker[2:5] if ticker[:2] == "SY" else None
    if area == 'OSL':
        area = "NO1"
    if area == "BER":
        area = "NO5"
    if area == "KRI":
        area = "NO2"
    if area == "TRH":
        area = "NO3"
    if area == "TRO":
        area = "NO4"
    instrument = "FUT" if ticker[:3] == "ENO" else "EPAD" if ticker[:2] == "SY" else None
    rec = {"ticker": ticker \
        , "area": area \
        , 'instrument': instrument \
        , "market": "Nasdaq OMX" \
        , "bid": str(df.loc[ticker_idx, "bid"]) \
        , "ask": str(df.loc[ticker_idx, "ask"]) \
        , "open": str(df.loc[ticker_idx, "open"]) \
        , "high": str(df.loc[ticker_idx, "high"]) \
        , "low": str(df.loc[ticker_idx, "low"]) \
        , "last": str(df.loc[ticker_idx, "last"]) \
        , "close": str(df.loc[ticker_idx, "close"]) \
        , "volume": str(0) \
        , "trading_date": str(df.loc[ticker_idx, "trading_date"]) \
        , "timestamp": str(df.loc[ticker_idx, "timestamp"])}
    print("Publishing", rec)
    mqttcli.publish("/marketdata/nordicpower/prices/nasdaqweb", json.dumps(rec))

def get_current_snapshot(api_conn):
    df = DerivativesApi.fetch_daily_prices(api_conn, "Nasdaq OMX", "Nordic Power", "ALL")
    print(df)
    return df


def pick_test_product():
    c = randrange(4)
    if c==0:
        return "ENOFUTBLQ1-24"
    elif c==1:
        return "ENOFUTBLQ4-23"
    elif c==2:
        return "ENOFUTBLYR-25"
    else:
        return "ENOFUTBLYR-26"



def simulate_price_changes(api_conn, mqttcli):
    df=get_current_snapshot(api_conn)
    df['bid'] = df['last']
    df['ask'] = df['last']
    while True:
        ticker_idx = randrange(len(df.index))

        tickrow=df.loc[df['ticker'] == pick_test_product()]
        ticker_idx=tickrow.index[0]

        ticker = df.loc[ticker_idx, 'ticker']


        v = random.uniform(-0.5, 0.5)
        type_change = randrange(4)
        if type_change==0:
            colname="high"
        elif type_change == 1:
            colname = "low"
        elif type_change == 2:
            colname = "last"
        else:
            colname="close"
        val = df.loc[ticker_idx, colname]
        val+=v
        dec_val = float("{:.2f}".format(val))
        df.loc[ticker_idx, colname]=dec_val
        print("Sending change for", ticker, colname, dec_val)
        generate_send_marketdata(mqttcli, df,ticker_idx,ticker)
        time.sleep(0.1)

if __name__ == '__main__':
    random.seed(datetime.now())
    api_conn=init_api()
    env = environ.Env()
    mqtt_broker = env.str('MQTT_HOST')
    mqtt_port= env.str('MQTT_WEBSOCKET_PORT')
    mqtt_usr=None if "MQTT_USERNAME" not in env else env.str("MQTT_USERNAME")
    mqtt_pwd = None if "MQTT_PASSWORD" not in env else env.str("MQTT_PASSWORD")
    mqttcli=MqttClient(mqtt_broker,mqtt_port,mqtt_usr,mqtt_pwd)
    mqttcli.connect(None, [], "Feed Sender")

    simulate_price_changes(api_conn, mqttcli)