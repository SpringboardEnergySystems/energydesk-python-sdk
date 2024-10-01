import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.risk.risk_api import RiskApi, RiskParameters
import pandas as pd

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])

def calc_volats(api_conn):
    df=RiskApi.calc_volatilities_df(api_conn, 12, ['NO1', 'NO2'])
    print(df)
import numpy as np
import scipy
def calc_covariance_var(api_conn):
    df,port_mean,port_stdev=RiskApi.calc_covariance_var_df(api_conn, 121, days_back=100)
    print(df)
    x = np.linspace(port_mean - 3 * port_stdev, port_mean + 3 * port_stdev, 40)
    pd = scipy.stats.norm.pdf(x, port_mean, port_stdev)
    print(x)
    print(pd)
    y11 = np.exp(-(x - port_mean) ** 2 / (2 * port_stdev ** 2)) / (np.sqrt(2 * np.pi * port_stdev ** 2))
    print(y11)

def calc_covariance_matrix(api_conn):
    df_covar=RiskApi.calc_covariance_matrix_df(api_conn,days_back=40)
    print(df_covar)

def rolling_products2(api_conn):
    res=RiskApi.get_rolling_products(api_conn,price_days=40)
    df_prices=pd.DataFrame(res['rolling_products'])
    print(df_prices)

import requests
def rolling_products():
    base_url = "https://hafslund-test.energydesk.no/appserver/staging"
    token="53ee077e6eafc01fa145ff938e681d6d1ced42f4"
    headers = {'Authorization': 'Token ' + token}
    full_url = base_url + "/api/riskmanager/rollingproducts/"
    payload={
        "price_days":40
    }
    response = requests.get(full_url, params=payload, headers=headers)
    print(response.status_code)
    if response.status_code ==200:
        df_prices = pd.DataFrame(response.json()['rolling_products'])
        print(df_prices)
    else:
        print("Error code ", response.status_code)

def test_update_riskparams(api_conn):
    res=RiskApi.get_risk_parameters(api_conn)
    print(res)
    rp=RiskParameters()
    rp.risk_free_rate=0.04
    rp.volatlity=0.33
    RiskApi.upsert_global_risk_parameters(api_conn, rp)

if __name__ == '__main__':

    api_conn=init_api()
    rolling_products()
    #calc_covariance_var(api_conn)

