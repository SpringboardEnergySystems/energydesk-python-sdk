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

def load_var_data(api_conn):

    data=RiskApi.get_var_portfolios(api_conn, {'trading_date':'2025-04-01'})
    print(data)
    return

    data = RiskApi.get_var_dates(api_conn, {'portfolio__id':122})
    print(data)
    data = RiskApi.get_var_portfolios_calculated(api_conn, {'trading_date':'2025-04-02'})
    print(data)
    # In this case a period is natural to look at
    params={'trading_date':'2025-04-02', 'portfolio__id':122}
    data=RiskApi.get_var_calculations(api_conn, params)
    print(data)
    data=RiskApi.get_var_calculations_compact(api_conn, params)
    print(data)
    data=RiskApi.get_var_calculations_embedded(api_conn, params)
    print(data)



def load_risk_data(api_conn):
    # In this case a period is natural to look at
    params={'trading_date__gte':'2025-02-10','trading_date__lt':'2025-02-11'}
    data=RiskApi.get_rolling_products_embedded(api_conn, params)
    #print(data)

    # In portal may require user to specify a date here so a full list is not returned - since they look at data per day for this API
    params={}
    data=RiskApi.get_product_returns(api_conn, params)
    #print(data)

    for rec in data['results']:
        returnsframe=pd.DataFrame(rec['returns_data'])
        print("Product returns for date {} df {} ".format(rec['trading_date'], returnsframe))

    # In portal may require user to specify a date here so a full list is not returned - since they look at data per day for this API
    params={'trading_date':'2025-03-19'}
    data=RiskApi.get_covariance_data(api_conn, params)
    for rec in data['results']:
        returnsframe=pd.DataFrame(rec['covariance_data'])
        print("Covariance data for date {} df {} ".format(rec['trading_date'], returnsframe))
        returnsframe=pd.DataFrame(rec['correlation_data'])
        print("Correlation data  for date {} df {} ".format(rec['trading_date'], returnsframe))

if __name__ == '__main__':

    api_conn=init_api()
    #load_risk_data(api_conn)
    load_var_data(api_conn)

