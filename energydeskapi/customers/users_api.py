import logging
import pandas as pd
from energydeskapi.sdk.common_utils import parse_enum_type
import json
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
        self.company=None
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
        if self.company is not None: dict['company'] = self.company
        if self.company_registry_number is not None: dict['company_registry_number'] = self.company_registry_number
        if self.is_super_user is not None: dict['is_super_user'] = self.is_super_user
        return dict

class UsersApi:
    """Class for user profiles and companies

    """

    @staticmethod
    def update_userprofile(api_connection, user):
        """Updates user profiles

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param user: object of user
        :type user: str, required
        """
        payload = user.get_dict()
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/customers/update-userprofile', payload)
        if json_res is None:
            logger.error("Problems updating user " + user.username)
            return False
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
        """Fetches API token

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
        """Fetches users from roles

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param user_role_enum: role of user
        :type user_role_enum: str, required
        """

        return UsersApi.get_users(api_connection, {"user_role__pk": parse_enum_type(user_role_enum)})

    @staticmethod
    def get_users_by_role_df(api_connection, user_role_enum):
        """Fetches users from roles and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param user_role_enum: role of user
        :type user_role_enum: str, required
        """
        return UsersApi.get_users_df(api_connection, {"user_role__pk": parse_enum_type(user_role_enum)})


    @staticmethod
    def get_profile_by_username(api_connection, username):
        """Fetches profile from username

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param username: username of user
        :type username: str, required
        """
        return UsersApi.get_users(api_connection, {"user__username": str(username)})

    def get_profile_by_key(api_connection, pk):
        """Fetches user profile from key

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param pk: personal key of profile
        :type pk: str, required
        """
        logger.info("Fetching profile with key " + str(pk))
        json_res=api_connection.exec_get_url('/api/customers/profiles/' + str(pk) + "/")
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_embedded_profile_by_key(api_connection, pk):
        payload = {"user__id": pk}

        json_res = api_connection.exec_get_url('/api/customers/profiles/embedded/', payload)
        result = json_res['results'][0]
        return result


    @staticmethod
    def process_dataframe(df):
        dfsubset = df.rename(columns={"pk":"pk",
                                      "user.username":"username",
                                      "user_role.description": "user_role",
                                      "user.email": "email",
                                      "user.first_name": "first_name",
                                      "user.last_name": "last_name",
                                      "company.name":"company"
                                      })

        return dfsubset[['pk', 'username', 'user_role', 'email', 'first_name', 'last_name', 'company']]

    @staticmethod
    def get_users_by_key_df(api_connection, user_profile_key):
        """Fetches user profile from key and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param user_profile_key: personal key of user profile
        :type user_profile_key: str, required
        """
        return UsersApi.get_profile_by_key(api_connection,user_profile_key)

    @staticmethod
    def get_user_by_key(api_connection, user_key):
        logger.info("Fetching user with key " + str(user_key))
        json_res = api_connection.exec_get_url('/api/customers/users/' + str(user_key) + "/")
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def update_user(api_connection, pk, payload ):
        """Fetches user profiles

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Updating user profile")
        print(payload)
        success, json_res, status_code, error_msg = api_connection.exec_patch_url('/api/customers/profiles/' + str(pk)  + "/", payload)
        if success is None:
            logger.error(error_msg)
        return success, json_res, status_code, error_msg

    @staticmethod
    def get_users(api_connection, parameters={}):
        """Fetches user profiles

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching user profile")
        json_res = api_connection.exec_get_url('/api/customers/profiles/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_users_embedded(api_connection, parameters={}):
        """Fetches user profiles
        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/customers/profiles/embedded/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_users_df2(api_connection, parameters={}):
        """Fetches user profiles

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching user profile")
        json_res = api_connection.exec_get_url('/api/customers/profiles/embedded/', parameters)
        if json_res is None:
            return None
        df = pd.json_normalize(json_res['results'], max_level=1)
        return UsersApi.process_dataframe(df)
    @staticmethod
    def get_users_df(api_connection, parameters={}):
        #json_res=UsersApi.get_users(api_connection, parameters)
        json_res = api_connection.exec_get_url('/api/customers/profiles/embedded/', parameters)
        if json_res is not None:
            dict=json.loads(json.dumps(json_res['results']))
            df = pd.json_normalize(dict, max_level=1)
            return UsersApi.process_dataframe(df)
        return None

    @staticmethod
    def create_users(api_connection, users):
        """Creates users from payload

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param users: payload of user profile containing username, email, firstname, lastname, user role and company registry number
        :type users: str, required
        """
        logger.info("Registering " + str(len(users) )+ " users")
        for user in users:
            payload=user.get_dict()
            success, json_res, status_code, error_msg=api_connection.exec_post_url('/api/customers/register-user', payload)
            if json_res is None:
                logger.error("Problems registering user "  + user.username)
            else:
                logger.info("User registered " + user.username)

    @staticmethod
    def get_user_roles_df(api_connection):
        """Fetches all user roles and displays in a dataframe

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
        """Fetches user from url

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param user_pk: personal key of user
        :type user_pk: str, required
        """
        return api_connection.get_base_url() + '/api/customers/profiles/' + str(user_pk) + "/"