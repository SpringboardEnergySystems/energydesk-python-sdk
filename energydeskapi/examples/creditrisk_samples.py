import json
import logging
from energydeskapi.creditrisk.creditrisk_api import CreditRiskApi
from energydeskapi.sdk.common_utils import init_api


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def get_creditrisk_types(api_conn):
    print(CreditRiskApi.get_governance_df(api_conn))
    print(CreditRiskApi.get_competivepos_df(api_conn))
    print(CreditRiskApi.get_capstructure_df(api_conn))
    print(CreditRiskApi.get_liquidity_df(api_conn))
    print(CreditRiskApi.get_diversification_df(api_conn))
    print(CreditRiskApi.get_comparableratings_df(api_conn))
    print(CreditRiskApi.get_financialpos_df(api_conn))
    print(CreditRiskApi.get_govinfluence_df(api_conn))


if __name__ == '__main__':

    api_conn = init_api()
    get_creditrisk_types(api_conn)
