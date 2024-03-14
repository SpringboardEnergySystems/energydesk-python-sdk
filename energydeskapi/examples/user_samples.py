import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.customers.users_api import UsersApi, User, UserGroup, UserFeatureAccess
from energydeskapi.customers.customers_api import CustomersApi
from energydeskapi.types.company_enum_types import UserRoleEnum
import pandas as pd
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])

def update_user_company(api_conn, user_name, company_regnmbr):
    users = UsersApi.get_users_embedded(api_conn)
    #dict=json.loads(users)
    for user in users['results']:
        if user['user']['username']==user_name:
            companies=CustomersApi.get_companies(api_conn, {'registry_number':company_regnmbr})
            if len(companies['results'])==0:
                logging.warning("No company with reg nmb" + company_regnmbr)
                return
            pkcomp=companies['results'][0]['pk']  #Assuming 1
            compurl=CustomersApi.get_company_url(api_conn, pkcomp)
            pkuser=user['user']['pk']
            profile = UsersApi.get_profile_by_key(api_conn,pkuser)
            profile['company']=compurl
            payload={"company":compurl}
            success, json_res, status_code, error_msg =UsersApi.update_user(api_conn,profile['pk'],payload)
            print("Profile updated", success)

    #print(users)
def list_users(api_conn):
    df=UsersApi.get_users_by_role(api_conn,UserRoleEnum.RISKMANAGER)
    print(df)
    df = UsersApi.get_users_by_role_df(api_conn, UserRoleEnum.RISKMANAGER)
    print(df)
    df = UsersApi.get_profile_by_key(api_conn,1)
    print(df)

def list_users_embedded(api_conn):
    payload = {'page_size': 200}
    df = UsersApi.get_users_embedded(api_conn)
    print(df)

def list_users_df(api_conn):
    payload = {'page_size':200}
    df = UsersApi.get_users_df(api_conn, payload)
    print(df)

def get_user_by_pk(api_conn):
    pk = 5
    json_user = UsersApi.get_user_by_key(api_conn, pk)
    print(json_user)

def get_profile_by_pk_embedded(api_conn):
    pk = 5
    json_profiles = UsersApi.get_embedded_profile_by_key(api_conn, pk)
    print(json_profiles)

def list_user_groups(api_conn):
    result = UsersApi.get_user_groups(api_conn)
    print(result)

def list_user_groups_df(api_conn):
    result = UsersApi.get_user_groups_df(api_conn)
    print(result)

def get_user_group_from_pk(api_conn):
    pk = 18
    result = UsersApi.get_user_group_by_key(api_conn, pk)
    print(result)

def list_users_in_user_group(api_conn):
    pk = 19
    result = UsersApi.get_users_from_user_group(api_conn, pk)
    print(result)

def list_users_in_user_group_embedded(api_conn):
    pk = 19
    result = UsersApi.get_users_from_user_group_embedded(api_conn, pk)
    print(result)

def list_user_feature_access(api_conn):
    params = {'group': 4,
              'system_feature': 2}
    result = UsersApi.get_user_feature_access(api_conn, params)
    print(result)

def list_user_feature_access_to_group(api_conn):
    group_pk = 19
    result = UsersApi.get_user_feature_access_for_user_group(api_conn, group_pk)
    print(result)

def create_user_feature_access(api_conn):
    uf = UserFeatureAccess()
    uf.pk = 6
    uf.group = "http://127.0.0.1:8001/api/customers/usergroups/19/"
    uf.system_feature = "http://127.0.0.1:8001/api/system/systemfeatures/1/"
    uf.system_access_type = "http://127.0.0.1:8001/api/system/systemaccesstypes/1/"
    result = UsersApi.upsert_user_feature_access(api_conn, uf)
    print(result)

def get_traders(api_conn):
    traders=UsersApi.get_users_df(api_conn, {'page_size':200})
    print(traders)

def del_user_feature_access(api_conn):
    pk = 7
    result = UsersApi.delete_user_feature_access(api_conn, pk)
    print(result)

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

def create_user_group(api_conn):
    ug = UserGroup()
    ug.pk = 20
    ug.users = [UsersApi.get_user_url(api_conn, 1), UsersApi.get_user_url(api_conn, 2), UsersApi.get_user_url(api_conn, 4)]
    result = UsersApi.upsert_user_groups(api_conn, ug)
    print(result)

def del_user_group(api_conn):
    pk = 16
    result = UsersApi.delete_user_groups(api_conn, pk)
    print(result)

def add_user_user_group(api_conn):
    user_group_pk = 20
    user = 4
    result = UsersApi.add_user_to_user_group(api_conn, user_group_pk, user)
    print(result)

def remove_user_user_group(api_conn):
    user_group_pk = 20
    user_pk = 4
    result = UsersApi.remove_user_from_user_group(api_conn, user_group_pk, user_pk)
    print(result)

def send_reset_password_email(api_conn):
    email = "morteb1507@gmail.com"
    UsersApi.send_password_reset_email(api_conn, email)

def reset_password(api_conn):
    password = "superbpasssssss312412"
    reset_token = "cc1ce950c5255d9"
    payload = {"password": password,
               "token": reset_token}
    UsersApi.reset_password(api_conn, payload)

def verify_token(api_conn):
    token = "f166277d2aecd06f30d6353b9c9bf5ce8dc"
    UsersApi.validate_reset_token(api_conn, token)

def basic_auth(api_conn):
    api_conn.validate_via_basic_auth("s.r.eriksen@gmail.com", "xxx")


if __name__ == '__main__':
    pd.set_option('display.max_rows', None)
    api_conn=init_api()
    #update_user_company(api_conn, "s.r.eriksen@gmail.com","976894677" )
    #update_user_company(api_conn, "steinar.eriksen@hafslundeco.no", "976894677")
    #get_user_by_pk(api_conn)
    #get_profile_by_pk_embedded(api_conn)
    #list_users_embedded(api_conn)
    #update_user_company(api_conn, "steinar.eriksen@hafslundeco.no", "922675163")
    #register_companies(api_conn)
    #create_company(api_conn)
    #create_user(api_conn)
    #send_reset_password_email(api_conn)
    #reset_password(api_conn)
    #verify_token(api_conn)
    #update_company(api_conn)
    #list_user_feature_access(api_conn)
    #list_user_groups(api_conn)
    #list_user_groups_df(api_conn)
    #get_user_group_from_pk(api_conn)
    #create_user_group(api_conn)
    #del_user_group(api_conn)
    #list_users_in_user_group(api_conn)
    #list_users_in_user_group_embedded(api_conn)
    #remove_user_user_group(api_conn)
    #add_user_user_group(api_conn)
    #create_user_feature_access(api_conn)
    list_users_df(api_conn)
    #del_user_feature_access(api_conn)
