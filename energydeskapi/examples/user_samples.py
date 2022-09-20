import sys

import requests
import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.customers.users_api import UsersApi, User
from energydeskapi.types.company_enum_types import CompanyTypeEnum, CompanyRoleEnum,UserRoleEnum

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])



def list_users(api_conn):
    df=UsersApi.get_users(api_conn)
    print(df)


def create_user(api_conn):
    u = User()
    u.username = "myuser@gmail.com"
    u.email = "myuser@gmail.com"
    u.first_name= "My"
    u.last_name = "User"
    u.user_role=UserRoleEnum.RISKMANAGER
    u.company_registry_number="666"
    print(u.get_dict())
    UsersApi.create_users(api_conn, [u])

if __name__ == '__main__':

    api_conn=init_api()
    user_profile=UsersApi.get_user_profile(api_conn)
    print(user_profile)
    #list_users(api_conn)
    #register_companies(api_conn)
    #create_company(api_conn)
    #create_user(api_conn)
    #update_company(api_conn)
