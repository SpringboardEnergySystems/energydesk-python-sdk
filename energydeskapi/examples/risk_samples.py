import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.risk.risk_api import RiskApi, RiskParameters


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
    df,port_mean,port_stdev=RiskApi.calc_covariance_var_df(api_conn, 9, days_back=40)
    print(df)
    x = np.linspace(port_mean - 3 * port_stdev, port_mean + 3 * port_stdev, 40)
    pd = scipy.stats.norm.pdf(x, port_mean, port_stdev)
    print(x)
    print(pd)
    y11 = np.exp(-(x - port_mean) ** 2 / (2 * port_stdev ** 2)) / (np.sqrt(2 * np.pi * port_stdev ** 2))
    print(y11)
def test_update_riskparams(api_conn):
    res=RiskApi.get_risk_parameters(api_conn)
    print(res)
    rp=RiskParameters()
    rp.risk_free_rate=0.04
    rp.volatlity=0.33
    RiskApi.upsert_global_risk_parameters(api_conn, rp)

if __name__ == '__main__':

    api_conn=init_api()
    calc_covariance_var(api_conn)

