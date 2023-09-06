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

def get_rated_companies(api_conn):

    res=CreditRiskApi.get_ratings(api_conn)
    for rec in res['results']:
        print(rec.keys())
        jrec=json.loads(rec['rating_data'])
        print(jrec.keys())


def calculate_rating(api_conn, company_regnumber):
    calc=CreditCalculation()
    res=CreditRiskApi.calculate_credit_rating(api_conn, company_regnumber, "NO", calc)
    print(res)
def save_rating(api_conn, company_regnumber):
    calc=CreditCalculation()
    res=CreditRiskApi.calculate_credit_rating(api_conn, company_regnumber, "NO", calc)
    CreditRiskApi.save_credit_rating(api_conn, company_regnumber, "NO", calc)

def get_annual_accounts(api_conn, company_regnumber):
    params={'company__registry_number':company_regnumber}
    res=CreditRiskApi.get_accounts(api_conn, params)
    print(res)

if __name__ == '__main__':

    api_conn = init_api()
    #get_annual_accounts(api_conn, "819449392")
    #save_rating(api_conn,"819449392")#"998753562")
    get_rated_companies(api_conn)
