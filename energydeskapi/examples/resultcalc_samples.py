import logging
import pendulum
from energydeskapi.results.results_api import ResultCalcParams
from energydeskapi.results.results_api import ResultsApi
from energydeskapi.sdk.common_utils import init_api

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def calculate_results(api_conn):
    portfolios = "127,128,129,344,130"
    currency="NOK"
    resolution="MONTHLY"
    trading_date=pendulum.today()
    rpar=ResultCalcParams(portfolios, trading_date, resolution, currency)
    success, json_res, status_code, error_msg  = ResultsApi.calculate_results(api_conn, rpar)
    print(json_res)


if __name__ == '__main__':
    api_conn = init_api()
    calculate_results(api_conn)
