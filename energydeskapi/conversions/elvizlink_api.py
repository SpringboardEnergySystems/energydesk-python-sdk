import logging
import requests
import environ
import json
from rauth import OAuth2Service
from energydeskapi.customers.customers_api import CustomersApi
from energydeskapi.customers.users_api import UsersApi
from energydeskapi.portfolios.tradingbooks_api import TradingBooksApi
logger = logging.getLogger(__name__)
#  Change
class ElvizLinksApi:
    """Class for converting elviz

    """
    @staticmethod
    def get_company_mappings(api_connection):
        """Fetches company mappings

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Looking up company mappings")
        return api_connection.exec_get_url('/api/elvizmapping/companies/')

    @staticmethod
    def lookup_company_mapping(api_connection, elviz_company_id):
        """Looks up company mapping from an elviz company id

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param elviz_company_id: id of an elviz company
        :type elviz_company_id: str, required
        """
        logger.info("Looking up company mapping with id " + str(elviz_company_id))
        json_res = api_connection.exec_get_url('/api/elvizmapping/companies/')
        for comp in json_res:
            if comp['elviz_company_id']==elviz_company_id:
                print("Found company ", comp)
                return comp
        return None
    @staticmethod
    def upsert_company_mapping(api_connection, registry_number, elviz_company_id, elviz_company_name):
        """Registers or updates a company mapping

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param registry_number: registry number of a company from brreg
        :type registry_number: str, required
        :param elviz_company_id: id of an elviz company
        :type elviz_company_id: str, required
        :param elviz_company_name: name of an elviz company
        :type elviz_company_name: str, required
        """
        logger.info("Register or update company mappingrs")
        company=CustomersApi.get_company_from_registry_number( api_connection,registry_number)
        if company is None:
            logger.error("Cannot map a company that is not stored internally with registry " + str(registry_number))
            return False

        comp_url=api_connection.get_base_url() + "/api/customers/companies/" + str(company['pk']) + "/"
        payload={"elviz_company_id":elviz_company_id,
                 "elviz_company_name": elviz_company_name,
                 "energydesk_company":comp_url}
        print("Updating " + str(payload))
        existing=ElvizLinksApi.lookup_company_mapping(api_connection, elviz_company_id)
        if existing is None:
            success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/elvizmapping/companies/',payload)
        else:
            success, json_res, status_code, error_msg = api_connection.exec_patch_url('/api/elvizmapping/companies/'
                                                     + str(existing['pk']) + "/", payload)
        print(json_res)
        return True

    @staticmethod
    def get_user_mappings(api_connection):
        """Fetches user mappings

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Looking up user mappings")
        return api_connection.exec_get_url('/api/elvizmapping/users/')

    @staticmethod
    def obtain_session():
        env = environ.Env()
        client_id = env.str('ELVIZ_CLIENT_ID')
        client_secret = env.str('ELVIZ_CLIENT_SECRET')
        scope = env.str('ELVIZ_SCOPE')
        tenantid=env.str('AZURE_TENANT')
        service = OAuth2Service(client_id=client_id,
                                client_secret=client_secret,
                                access_token_url="https://login.microsoftonline.com/" + tenantid + "/oauth2/v2.0/token",
                                authorize_url="https://login.microsoftonline.com/" +  tenantid  + "/oauth2/v2.0/authorize",
                                base_url="https://graph.microsoft.com/oidc/userinfo")
        data = {'grant_type': 'client_credentials',
                'scope': scope,
                }
        auth_session = service.get_auth_session(data=data, decoder=json.loads)
        return auth_session

    @staticmethod
    def lookup_user_mapping(api_connection, elviz_user_id):
        """Looks up user mapping from an elviz user id

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param elviz_user_id: id of an elviz user
        :type elviz_user_id: str, required
        """
        logger.info("Looking up users mapping with id " + str(elviz_user_id))
        json_res = api_connection.exec_get_url('/api/elvizmapping/users/')
        for comp in json_res:
            if comp['elviz_user_id'] == elviz_user_id:
                print("Found user ", comp)
                return comp
        return None

    @staticmethod
    def upsert_user_mapping(api_connection, enegydesk_username, elviz_user_id, elviz_userr_name):
        """Registers or updates a user mapping

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param enegydesk_username: username of an energydesk user
        :type enegydesk_username: str, required
        :param elviz_user_id: id of an elviz user
        :type elviz_user_id: str, required
        :param elviz_userr_name: username of an elviz user
        :type elviz_userr_name: str, required
        """
        logger.info("Register or update user mapping")
        edeskuser = UsersApi.get_profile_by_username(api_connection, enegydesk_username)
        if edeskuser is None:
            logger.error("Cannot map a user that is not stored internally with name " + str(enegydesk_username))
            return False

        profile_url = api_connection.get_base_url() + "/api/customers/profiles/" + str(edeskuser['results'][0]['pk']) + "/"
        payload = {"elviz_user_id": elviz_user_id,
                   "elviz_user_name": elviz_userr_name,
                   "energydesk_profile": profile_url}
        existing = ElvizLinksApi.lookup_user_mapping(api_connection, enegydesk_username)
        if existing is None:
            success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/elvizmapping/users/', payload)
        else:
            success, json_res, status_code, error_msg = api_connection.exec_patch_url('/api/elvizmapping/users/'
                                                     + str(existing['pk']) + "/", payload)
        print(json_res)
        return True


    @staticmethod
    def get_portfolio_mappings(api_connection):
        """Fetches portfolio mappings

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Looking up portfolio mappings")
        return api_connection.exec_get_url('/api/elvizmapping/portfolios/')

    @staticmethod
    def lookup_tadingbook(api_connection, tradingbook_name):
        """Looks up tradingbooks from name

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param tradingbook_name: name of a tradingbook
        :type tradingbook_name: str, required
        """
        logger.info("Looking up tradingbook " + str(tradingbook_name))
        df = TradingBooksApi.get_tradingbooks_df(api_connection)
        #print(df)
        for index,row in df.iterrows():
            if row['description'] == tradingbook_name:
                print("Found tradingbook_name ", tradingbook_name)
                return row['pk']
        print("Did not find", tradingbook_name)
        return None

    @staticmethod
    def lookup_portfolio_mapping(api_connection, elviz_portfolio_id):
        """Looks up portfolio mappings from elviz portfolio id

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param elviz_portfolio_id: id of an elviz portfolio
        :type elviz_portfolio_id: str, required
        """
        logger.info("Looking up users mapping with id " + str(elviz_portfolio_id))
        json_res = api_connection.exec_get_url('/api/elvizmapping/portfolios/')
        for comp in json_res:
            if comp['elviz_portfolio_id'] == elviz_portfolio_id:
                print("Found portfolio ", comp)
                return comp
        return None
    @staticmethod
    def upsert_portfolio_mapping(api_connection, tradingbook, elviz_portfolio_id, elviz_portfolio_name):
        """Registers or updates a portfolio mapping

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param tradingbook: name of a tradingbook
        :type tradingbook: str, required
        :param elviz_portfolio_id: id of an elviz portfolio
        :type elviz_portfolio_id: str, required
        :param elviz_portfolio_name: name of an elviz portfolio
        :type elviz_portfolio_name: str, required
        """
        logger.info("Register or update user mapping")
        edeskbook = ElvizLinksApi.lookup_tadingbook(api_connection, tradingbook)
        if edeskbook is None:
            logger.error("Cannot map a portfolio that is not stored internally with name " + str(tradingbook))
            return False

        tbook_url=TradingBooksApi.get_tradingbook_url(api_connection, edeskbook)
        payload = {"elviz_portfolio_id": elviz_portfolio_id,
                   "elviz_portfolio_name": elviz_portfolio_name,
                   "energydesk_trading_book": tbook_url}
        existing = ElvizLinksApi.lookup_portfolio_mapping(api_connection, elviz_portfolio_id)
        print(existing)
        if existing is None:
            success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/elvizmapping/portfolios/', payload)
        else:
            success, json_res, status_code, error_msg = api_connection.exec_patch_url('/api/elvizmapping/portfolios/'
                                                     + str(existing['pk']) + "/", payload)
        print(json_res)
        return True

    @staticmethod
    def exec_post_elvizapi(user_mappings, company_mappings, portfolio_mappings, days_back):
        env = environ.Env()
        server_url = None if 'ELVIZ_PROXY' not in env else env.str('ELVIZ_PROXY') + "/api/elviztrades"
        logger.info("Calling URL " + str(server_url))
        payload={
            "user_mappings": user_mappings,
            "portfolio_mappings": portfolio_mappings,
            "company_mappings": company_mappings,
            "days_back": days_back
        }
        logger.debug("...with payload " + str(payload) )

        h = {'Authorization': 'Bearer', 'Accept': 'application/json'}
        authsess = ElvizLinksApi.obtain_session()
        response = authsess.post(server_url, headers=h, data=json.dumps(payload))
        return response.json()

    @staticmethod
    def get_latest_elviz_trades(api_connection, days_back=1):
        port_maps=ElvizLinksApi.get_portfolio_mappings(api_connection)
        usr_maps=ElvizLinksApi.get_user_mappings(api_connection)
        comp_maps=ElvizLinksApi.get_company_mappings(api_connection)
        open("./usermappings.json", "w").write(usr_maps)
        open("./companymappings.json", "w").write(comp_maps)
        open("./portfolioappings.json", "w").write(port_maps)
        print(usr_maps,comp_maps,port_maps)
        elviz_trades = ElvizLinksApi.exec_post_elvizapi(usr_maps,comp_maps,port_maps, days_back )
        return elviz_trades

