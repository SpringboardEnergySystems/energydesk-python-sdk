
import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.customers.customers_api import CustomersApi, Company
from energydeskapi.types.company_enum_types import CompanyTypeEnum, CompanyRoleEnum

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def query_companies(api_conn):
    param={"id":711,
           "page_size":1}
    json_companies=CustomersApi.get_companies(api_conn, param)
    print(json_companies)



def query_company_types(api_conn):
    df=CustomersApi.get_company_types_df(api_conn)
    print(df)

def query_company_pk_by_name(api_conn):
    comp_name = "Arna Kraftselskap AS"
    json_companies = CustomersApi.get_company_pk_by_name(api_conn, comp_name)
    print(json_companies)

def query_company_by_pk(api_conn):
    comp_pk = 711
    json_companies = CustomersApi.get_company_by_key(api_conn, comp_pk)
    print(json_companies)

def load_company_from_regnumber(api_conn):
    regnumber = "982974011"
    json_companies=CustomersApi.get_company_from_registry_number(api_conn, regnumber)
    param = {"registry_number": regnumber}
   # json_companies = CustomersApi.get_companies(api_conn, param)
    print(json_companies)

def query_company_status(api_conn):
    status = "1"
    json_companies=CustomersApi.get_company_status(api_conn, status)
    print(json_companies)

def list_users(api_conn):
    df=CustomersApi.get_users(api_conn)
    print(df)


def create_company(api_conn):
    c = Company()
    c.name = "rørlegger AS"
    c.registry_number = "146389752"
    c.company_type = CustomersApi.get_company_type_url(api_conn, CompanyTypeEnum.SERVICE_COMPANY)
    c.company_roles = [CustomersApi.get_company_role_url(api_conn, CompanyRoleEnum.BRP)]
    c.address = "rørleggergata 43"
    c.postal_code = "0723"
    c.city = "Oslo"
    c.country = ""
    c.location = "65.436824,10.982431"
    # print(c.get_dict())
    CustomersApi.create_companies(api_conn, [c])


def update_company(api_conn):
    c = Company()
    c.pk=717  # Important to specify key of existing company being updated
    c.name = "fliselegger AS"
    c.registry_number = "146389752"
    c.company_type = CustomersApi.get_company_type_url(api_conn, CompanyTypeEnum.SERVICE_COMPANY)
    c.company_roles = [CustomersApi.get_company_role_url(api_conn, CompanyRoleEnum.BRP)]
    c.address = "rørleggergata 43"
    c.postal_code = "0723"
    c.city = "Oslo"
    c.country = ""
    c.location = "65.436824,10.982431"
    # print(c.get_dict())
    CustomersApi.update_company(api_conn, c)

if __name__ == '__main__':

    api_conn=init_api()
    #user_profile=CustomersApi.get_user_profile(api_conn)
    #print(user_profile)
    #list_users(api_conn)
    #register_companies(api_conn)
    #create_company(api_conn)
    query_companies(api_conn)
    #query_company_by_pk(api_conn)
    #load_company_from_regnumber(api_conn)
    #query_company_pk_by_name(api_conn)
    #query_company_status(api_conn)
    #update_company(api_conn)
