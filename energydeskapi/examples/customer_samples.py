import sys

import requests
import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.customers.customer_api import CustomerApi

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def query_companies(api_conn):
    json_companies=CustomerApi.get_companies(api_conn)
    all_companies_df=CustomerApi.get_companies_ext_df(api_conn)
    print(all_companies_df)


def query_company_types(api_conn):
    df=CustomerApi.get_company_types_df(api_conn)
    print(df)

def load_company_from_regnumber(api_conn, regnumber):
    comp=CustomerApi.get_company_from_registry_number(api_conn, regnumber)
    print(comp)

def list_users(api_conn):
    df=CustomerApi.get_users(api_conn)
    print(df)


def register_companies(api_conn):
    company_json = {
        'company_name': 'vennlig company',
        'company_type': 'Utility',
        'registry_number': '12126127821762'
    }
    df = CustomerApi.register_company(api_conn, company_json)
    print(df)


if __name__ == '__main__':

    api_conn=init_api()
    #user_profile=CustomerApi.get_user_profile(api_conn)
    #print(user_profile)
    #list_users(api_conn)
    #register_companies(api_conn)
    load_company_from_regnumber(api_conn, "995550164")
