import requests
import json
import logging
import pandas as pd
logger = logging.getLogger(__name__)


class User:
    def __init__(self):
        self.pk=0
        self.username=None
        self.email=None
        self.first_name=None
        self.last_name=None
        self.user_role = None
        self.is_super_user=False
        self.company_registry_number=None

    def get_dict(self):
        dict = {}
        role_pk =  self.user_role if isinstance( self.user_role, int) else  self.user_role.value
        dict['pk']=self.pk
        if self.username is not None: dict['username'] = self.username
        if self.email is not None: dict['email'] = self.email
        if self.first_name is not None: dict['first_name'] = self.first_name
        if self.last_name is not None: dict['last_name'] = self.last_name
        if self.user_role is not None: dict['user_role'] = role_pk
        if self.company_registry_number is not None: dict['company_registry_number'] = self.company_registry_number
        if self.is_super_user is not None: dict['is_super_user'] = self.is_super_user
        return dict

class UsersApi:
    """Class for user profiles and companies

    """

    @staticmethod
    def update_userprofile(api_connection, user):
        payload = user.get_dict()
        json_res = api_connection.exec_post_url('/api/customers/update-userprofile', payload)
        if json_res is None:
            logger.error("Problems updating user " + user.username)
            False
        else:
            logger.info("User profile updated " + user.username)
            return True

    @staticmethod
    def get_user_profile(api_connection):
        """Fetches user profile

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching user profile")
        json_res=api_connection.exec_get_url('/api/energydesk/get-user-profile/')
        if json_res is not None:
            return json_res
        return None

    @staticmethod
    def get_api_token(api_connection):
        """Fetches user profile

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching API token")
        json_res=api_connection.exec_get_url('/api/energydesk/get-api-token/')
        if json_res is not None:
            return json_res
        return None

    @staticmethod
    def get_users_by_role(api_connection, user_role_enum):
        """Fetches user profile

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        role_pk = user_role_enum if isinstance(user_role_enum, int) else user_role_enum.value

        logger.info("Fetching users by role ")
        json_res=api_connection.exec_post_url('/api/customers/userprofiles-by-role', payload={"user_role_enum": str(role_pk)})
        if json_res is not None:
            return json_res
        return None

    @staticmethod
    def get_users_by_role_df(api_connection, user_role_enum):
        dict=UsersApi.get_users_by_role(api_connection, user_role_enum)
        if dict is not None:
            df = pd.DataFrame(data=dict)
            return df
        return None

    @staticmethod
    def get_profile_by_key(api_connection, pk):
        """Fetches a specific company as long as the user has rights

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching profile with key " + str(pk))
        json_res=api_connection.exec_post_url('/api/customers/userprofiles-by-key', payload={"profile_key": str(pk)})
        if json_res is None:
            return None
        return json_res[0]

    @staticmethod
    def get_users_by_key_df(api_connection, user_profile_key):
        dict=UsersApi.get_profile_by_key(api_connection, user_profile_key)
        if dict is not None:
            df = pd.DataFrame(data=dict)
            return df
        return None

    @staticmethod
    def get_users(api_connection):
        """Fetches user profile

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching user profile")
        json_res=api_connection.exec_get_url('/api/customers/profiles')
        if json_res is not None:
            df = pd.DataFrame(data=json_res)
            return df
        return None

    @staticmethod
    def create_users(api_connection, users):
        """Fetches user profile

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Registering " + str(len(users) )+ " users")
        for user in users:
            payload=user.get_dict()
            json_res=api_connection.exec_post_url('/api/customers/register-user', payload)
            if json_res is None:
                logger.error("Problems registering user "  + user.username)
            else:
                logger.info("User registered " + user.username)

    @staticmethod
    def get_user_roles_df(api_connection):
        """Fetches all company types in system with basic key+ name infmation

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching user roles")
        json_res=api_connection.exec_get_url('/api/customers/userroles/')
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def get_user_url(api_connection, user_pk):
        return api_connection.get_base_url() + '/api/customers/profiles/' + str(user_pk) + "/"