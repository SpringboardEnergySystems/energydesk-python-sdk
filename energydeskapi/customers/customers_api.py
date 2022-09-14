import requests
import json
import logging
import pandas as pd
logger = logging.getLogger(__name__)


class Company:
    def __init__(self):
        self.pk=0
        self.name=None
        self.registry_number=""
        self.company_type=None
        self.company_roles=None
        self.address=None
        self.postal_code=""
        self.city=None
        self.country=None
        self.location="0,0"

    def get_dict(self):
        dict = {}
        dict['pk']=self.pk
        if self.name is not None: dict['name'] = self.name
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
    def get_user_profile(api_connection):
        """Fetches user profile

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching user profile")
        json_res=api_connection.exec_get_url('/api/energydesk/getuserprofile/')
        if json_res is not None:
            return json_res
        return None

    @staticmethod
    def get_users(api_connection):
        """Fetches user profile

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching user profile")
        json_res=api_connection.exec_get_url('/api/customers/users/traders')
        if json_res is not None:
            df = pd.DataFrame(data=json_res)
            return df
        return None

    @staticmethod
    def update_company(api_connection, company):
        payload = company.get_dict()
        json_res = api_connection.exec_patch_url('/api/customers/company/', payload)
        if json_res is None:
            logger.error("Problems updating company " + company.name)
        else:
            logger.info("Company updated " + company.name)

    @staticmethod
    def create_companies(api_connection, companies):
        """ Registers assets

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param companies: list of companies
        :type companies: str, required
        """
        logger.info("Registering " + str(len(companies) )+ " companies")
        for company in companies:
            payload=company.get_dict()
            json_res=api_connection.exec_post_url('/api/customers/company/', payload)
            if json_res is None:
                logger.error("Problems registering company "  + company.name)
            else:
                logger.info("Company registered " + company.name)

    # This should e identical to create_assets (i.e. create_companies) taking a list of class Company
    # def create_companies(api_connection, companies): looping through companies and getting get_dict() to insert into API
    def register_company(api_connection, company):
        json_res = api_connection.exec_post_url('/api/customers/register_company', company)
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
        json_res=api_connection.exec_get_url('/api/customers/companytype/')
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def get_companies_ext_df(api_connection):
        """Fetches all companies in system with basic key+ name infmation

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching companylist")
        json_res=api_connection.exec_get_url('/api/customers/get_all_companies')
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res["companies"])
        return df

    @staticmethod
    def get_company_by_name(api_connection, company_name):
        df = CustomerApi.get_companies_ext_df(api_connection)
        dfres = df.loc[df['company_name'] == company_name]
        if len(dfres.index)==0:
            logger.warning("No company named " + str(company_name))
            return None
        comppk = dfres['pk'].values[-1]
        return comppk


    @staticmethod
    def get_companies(api_connection):
        """Fetches all company objects with URL relations. Will only return companies for which the user has rights

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching company list")
        json_res=api_connection.exec_get_url('/api/customers/company')
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_company_type_url(api_connection, company_type_enum):
        return api_connection.get_base_url() + '/api/customers/companytype/' + str(company_type_enum.value) + "/"

    @staticmethod
    def get_company_role_url(api_connection, company_role_enum):
        return api_connection.get_base_url() + '/api/customers/companyrole/' + str(company_role_enum.value) + "/"

    @staticmethod
    def get_company_url(api_connection, company_pk):
        return api_connection.get_base_url() + '/api/customers/company/' + str(company_pk) + "/"

    @staticmethod
    def get_country_url(api_connection, country_pk):
        return api_connection.get_base_url() + '/api/customers/country/' + str(country_pk) + "/"

    @staticmethod
    def get_company_from_registry_number(api_connection, registry_number):
        """Fetches all company objects with URL relations. Will only return companies for which the user has rights

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res=api_connection.exec_get_url('/api/customers/company_from_registry_number?registry_number=' + registry_number )
        if json_res is None:
            return None
        return json_res