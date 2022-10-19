import requests
import json
import logging
import pandas as pd
logger = logging.getLogger(__name__)


class Company:
    def __init__(self):
        self.pk=0
        self.name=None
        self.alias = None
        self.lei_code = None
        self.registry_number=""
        self.company_type=None
        self.company_roles=None
        self.address=""
        self.postal_code=""
        self.city=""
        self.country=""
        self.location="0,0"

    def get_dict(self):
        dict = {}
        dict['pk']=self.pk
        if self.name is not None: dict['name'] = self.name
        if self.alias is not None: dict['alias'] = self.alias
        if self.lei_code is not None: dict['lei_code'] = self.lei_code
        if self.registry_number is not None: dict['registry_number'] = self.registry_number
        if self.company_type is not None: dict['company_type'] = self.company_type
        if self.company_roles is not None: dict['company_roles'] = self.company_roles
        if self.address is not None: dict['address'] = self.address
        if self.postal_code is not None: dict['postal_code'] = self.postal_code
        if self.city is not None: dict['city'] = self.city
        if self.country is not None: dict['country'] = self.country
        if self.location is not None: dict['location'] = self.location
        return dict

class CustomersApi:
    """Class for user profiles and companies

    """


    @staticmethod
    def update_company(api_connection, company):
        """Updates companies

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param company: company object
        :type company: str, required
        """
        payload = company.get_dict()
        success, json_res, status_code, error_msg = api_connection.exec_patch_url('/api/customers/companies/' + str(company.pk) + "/", payload)
        if json_res is None:
            logger.error("Problems updating company " + company.name)
        else:
            logger.info("Company updated " + company.name)

    @staticmethod
    def create_companies(api_connection, companies):
        """Registers companies

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param companies: list of companies
        :type companies: str, required
        """
        logger.info("Registering " + str(len(companies) )+ " companies")
        for company in companies:
            payload=company.get_dict()
            success, json_res, status_code, error_msg=api_connection.exec_post_url('/api/customers/companies/', payload)
            if json_res is None:
                logger.error("Problems registering company "  + company.name)
            else:
                logger.info("Company registered " + company.name)

    # This should e identical to create_assets (i.e. create_companies) taking a list of class Company
    # def create_companies(api_connection, companies): looping through companies and getting get_dict() to insert into API
    def register_company(api_connection, company):
        """Registers company

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param company: company
        :type company: str, required
        """
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/customers/register-company', company)
        if json_res is None:
            return False
        print(json_res)
        return json_res["Registration"]

    @staticmethod
    def get_company_types_df(api_connection):
        """Fetches all company types in system with basic key+ name infmation

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching company types")
        json_res=api_connection.exec_get_url('/api/customers/companytypes/')
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def get_companies(api_connection, parameters={}):
        """Fetches all companies

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res=api_connection.exec_get_url('/api/customers/companies/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_company_roles_df(api_connection):
        """Fetches all company roles in system with basic key+ name infmation

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching company roles")
        json_res=api_connection.exec_get_url('/api/customers/companyroles/')
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def get_companies_df(api_connection, parameters={}):
        """Fetches all companies in system with basic key+ name infmation

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching companylist")
        parameters['page_size']=1000
        json_res=CustomersApi.get_companies(api_connection, parameters)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res["results"])
        return df

    @staticmethod
    def get_company_pk_by_name(api_connection, company_name):
        """Fetches companies from name

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param company_name: name of a company
        :type company_name: str, required
        """
        parameters={
           "name":company_name
        }
        res=CustomersApi.get_companies(api_connection, parameters)
        if res is None or len(res)==0:
            return 0
        company_key = res['results'][0]['pk']
        return company_key

    @staticmethod
    def get_company_by_key(api_connection, pk):
        """Fetches a specific company as long as the user has rights

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param pk: personal key of company
        :type pk: str, required
        """
        logger.info("Fetching company with key " + str(pk))
        json_res=api_connection.exec_get_url('/api/customers/companies/' + str(pk) + "/")
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_company_type_url(api_connection, company_type_enum):
        """Fetches url for company types from enum value

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param company_type_enum: type of company
        :type company_type_enum: str, required
        """
        # Will accept both integers of the actual enum type
        type_pk = company_type_enum if isinstance(company_type_enum, int) else company_type_enum.value
        return api_connection.get_base_url() + '/api/customers/companytypes/' + str(type_pk) + "/"

    @staticmethod
    def get_company_role_url(api_connection, company_role_enum):
        """Fetches url for company roles from enum value

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param company_role_enum: role of company
        :type company_role_enum: str, required
        """
        return api_connection.get_base_url() + '/api/customers/companyroles/' + str(company_role_enum.value) + "/"

    @staticmethod
    def get_company_url(api_connection, company_pk):
        """Fetches url for companies from pk

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param company_pk: personal key of company
        :type company_pk: str, required
        """
        return api_connection.get_base_url() + '/api/customers/companies/' + str(company_pk) + "/"

    @staticmethod
    def get_country_url(api_connection, country_pk):
        """Fetches url for countries from pk

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param country_pk: personal key of country
        :type country_pk: str, required
        """
        return api_connection.get_base_url() + '/api/customers/countries/' + str(country_pk) + "/"

    @staticmethod
    def get_company_from_registry_number(api_connection, registry_number):
        """Fetches all company objects with URL relations. Will only return companies for which the user has rights

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        param = {"registry_number": registry_number}
        json_res = CustomersApi.get_companies(api_connection, param)
        #json_res=api_connection.exec_get_url('/api/customers/companies-by-registrynumber?registry_number=' + registry_number )
        if json_res is not None:
            if len(json_res['results'])==0:
                return None
            return json_res['results'][0]
        return None

    @staticmethod
    def get_company_status(api_connection, status):
        """Fetches companies based on if they're active or not

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        param = {"is_active": status}
        json_res = CustomersApi.get_companies(api_connection, param)
        if json_res is None:
            return None
        return json_res