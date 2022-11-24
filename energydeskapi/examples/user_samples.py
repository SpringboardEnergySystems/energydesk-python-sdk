import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.customers.users_api import UsersApi, User
from energydeskapi.customers.customers_api import CustomersApi
from energydeskapi.types.company_enum_types import UserRoleEnum

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

def basic_auth(api_conn):
    api_conn.validate_via_basic_auth("s.r.eriksen@gmail.com", "xxx")


if __name__ == '__main__':

    api_conn=init_api()
    update_user_company(api_conn, "s.r.eriksen@gmail.com","976894677" )
    update_user_company(api_conn, "steinar.eriksen@hafslundeco.no", "976894677")
    #update_user_company(api_conn, "steinar.eriksen@hafslundeco.no", "922675163")
    #register_companies(api_conn)
    #create_company(api_conn)
    #create_user(api_conn)
    #update_company(api_conn)
