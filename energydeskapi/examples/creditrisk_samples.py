import json
import logging
from energydeskapi.creditrisk.creditrisk_api import CreditRiskApi, CreditCalculation
from energydeskapi.sdk.common_utils import init_api


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def get_creditrisk_types_df(api_conn):
    print(CreditRiskApi.get_governance_df(api_conn))
    print(CreditRiskApi.get_competivepos_df(api_conn))
    print(CreditRiskApi.get_capstructure_df(api_conn))
    print(CreditRiskApi.get_liquidity_df(api_conn))
    print(CreditRiskApi.get_diversification_df(api_conn))
    print(CreditRiskApi.get_comparableratings_df(api_conn))
    print(CreditRiskApi.get_financialpos_df(api_conn))
    print(CreditRiskApi.get_govinfluence_df(api_conn))

def get_creditrisk_types(api_conn):
    print(CreditRiskApi.get_governance(api_conn))
    print(CreditRiskApi.get_competivepos(api_conn))
    print(CreditRiskApi.get_capstructure(api_conn))
    print(CreditRiskApi.get_liquidity(api_conn))
    print(CreditRiskApi.get_diversification(api_conn))
    print(CreditRiskApi.get_comparableratings(api_conn))
    print(CreditRiskApi.get_financialpos(api_conn))
    print(CreditRiskApi.get_govinfluence(api_conn))

from energydeskapi.creditrisk.creditrisk_api import CreditRiskApi, CreditCalculation
def calculate_rating(api_conn, company_regnumber):
    calc=CreditCalculation()
    calc.liquidity=0 # etc
    res=CreditRiskApi.calculate_credit_rating(api_conn, company_regnumber, "NO", calc)
    print(res)
if __name__ == '__main__':

    api_conn = init_api()
    #get_creditrisk_types(api_conn)
    calculate_rating(api_conn,"998753562")
