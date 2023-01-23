import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.risk.risk_api import RiskApi


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])

def calc_volats(api_conn):
    df=RiskApi.calc_volatilities_df(api_conn, 12, ['NO1', 'NO2'])
    print(df)

def calc_covariance_var(api_conn):
    df=RiskApi.calc_covariance_var(api_conn, [11], days_back=40)

if __name__ == '__main__':

    api_conn=init_api()
    calc_covariance_var(api_conn)

