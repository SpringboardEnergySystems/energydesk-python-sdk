import sys

import requests
import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.clearing.clearing_api import ClearingApi
from energydeskapi.types.company_enum_types import CompanyTypeEnum, CompanyRoleEnum

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def fetch_clearing_reports(api_conn):
    df=ClearingApi.get_clearing_reports(api_conn)
    print(df)

def fetch_clearing_report_types(api_conn):
    df=ClearingApi.get_clearing_report_types(api_conn)
    print(df)


if __name__ == '__main__':

    api_conn=init_api()
    #user_profile=CustomersApi.get_user_profile(api_conn)
    #print(user_profile)
    #list_users(api_conn)
    #register_companies(api_conn)
    #create_company(api_conn)
    fetch_clearing_report_types(api_conn)
    #update_company(api_conn)
