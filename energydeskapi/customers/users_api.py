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
        #role_pk =  self.user_role if isinstance( self.user_role, int) else  self.user_role.value
        dict['pk']=self.pk
        if self.username is not None: dict['username'] = self.username
        if self.email is not None: dict['email'] = self.email
        if self.first_name is not None: dict['first_name'] = self.first_name
        if self.last_name is not None: dict['last_name'] = self.last_name
        if self.user_role is not None: dict['user_role'] = self.user_role
        if self.company is not None: dict['company'] = self.company
        if self.company_registry_number is not None: dict['company_registry_number'] = self.company_registry_number
        if self.is_super_user is not None: dict['is_super_user'] = self.is_super_user
        return dict

class UserGroup:
    def __init__(self):
        self.pk=0
        self.description=None
        self.users=[]

    def get_dict(self):
        dict = {}
        dict['pk']=self.pk
        if self.description is not None: dict['description'] = self.description
        if self.users is not None: dict['users'] = self.users
        return dict


class UserFeatureAccess:
    def __init__(self):
        self.pk=0
        self.group=None
        self.system_feature=None
        self.system_access_type=None

    def get_dict(self):
        dict = {}
        dict['pk']=self.pk
        if self.group is not None: dict['group'] = self.group
        if self.system_feature is not None: dict['system_feature'] = self.system_feature
        if self.system_access_type is not None: dict['system_access_type'] = self.system_access_type
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
        else:
            logger.info("User profile updated " + user.username)
        return success, json_res, status_code, error_msg

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

    @staticmethod
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
    def get_user_by_key(api_connection, pk):
        """Fetches user from key

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param pk: personal key of user
        :type pk: str, required
        """
        logger.info("Fetching user with key " + str(pk))
        json_res = api_connection.exec_get_url('/api/customers/users/' + str(pk) + "/")
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
        success, json_res, status_code, error_msg = api_connection.exec_patch_url('/api/customers/profiles/' + str(pk)  + "/", payload.get_dict())
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
            print(payload)
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
    def get_user_groups(api_connection):
        """Fetches user groups

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching user groups")
        json_res = api_connection.exec_get_url('/api/customers/usergroups/')
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_user_groups_df(api_connection):
        """Fetches user groups and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching user groups")
        json_res = api_connection.exec_get_url('/api/customers/usergroups/')
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def get_user_group_by_key(api_connection, pk):
        """Fetches user groups

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param pk: user group key
        :type pk: str, required
        """
        logger.info("Fetching user group " + str(pk))
        json_res = api_connection.exec_get_url('/api/customers/usergroups/' + str(pk) + '/')
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_users_from_user_group(api_connection, pk):
        """Fetches users from user groups

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param pk: user group key
        :type pk: str, required
        """
        logger.info("Fetching users from user group " + str(pk))
        json_res = api_connection.exec_get_url('/api/customers/usergroups/' + str(pk) + '/')
        if json_res is None:
            return None
        users = json_res['users']
        return users

    @staticmethod
    def get_users_from_user_group_embedded(api_connection, pk):
        """Fetches users from user groups with embedding

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param pk: user group key
        :type pk: str, required
        """
        logger.info("Fetching users from user group " + str(pk))
        json_res = api_connection.exec_get_url('/api/customers/usergroups/' + str(pk) + '/retrieve_embedded/')
        if json_res is None:
            return None
        users = json_res['users']
        return users

    @staticmethod
    def upsert_user_groups(api_connection, user_group):
        """Creates/Updates user groups

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param user_group: user group object
        :type user_group: str, required
        """
        logger.info("Upserting user group")
        payload = user_group.get_dict()
        key = int(payload['pk'])
        if key > 0:
            success, returned_data, status_code, error_msg = api_connection.exec_patch_url(
                '/api/customers/usergroups/' + str(payload['pk']) + "/", payload)
        else:
            success, returned_data, status_code, error_msg = api_connection.exec_post_url(
                '/api/customers/usergroups/', payload)
        if success:
            return returned_data
        return None

    @staticmethod
    def delete_user_groups(api_connection, pk):
        """Deletes user groups

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param pk: user group key
        :type pk: str, required
        """
        logger.info("Deleting user group")
        success, returned_data, status_code, error_msg = api_connection.exec_delete_url('/api/customers/usergroups/' + str(pk) + '/')
        if success:
            return "User group successfully deleted", status_code
        logger.error("User group has users and can't be deleted")
        return "User group has users and can't be deleted", status_code

    @staticmethod
    def add_user_to_user_group(api_connection, group_pk, user_pk):
        """Removes users from user group

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param group_pk: user group key
        :type group_pk: str, required
        :param user_pk: user profile key
        :type user_pk: str, required
        """
        logger.info("Adding user to user group")
        payload = {"user_group": group_pk,
                   "users": user_pk}
        success, returned_data, status_code, error_msg = api_connection.exec_post_url(
            '/api/customers/usergroups/add_user/', payload)
        if success:
            return "User successfully added to user group", status_code
        return None

    @staticmethod
    def remove_user_from_user_group(api_connection, group_pk, user_pk):
        """Removes users from user group

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param group_pk: user group key
        :type group_pk: str, required
        :param user_pk: user profile key
        :type user_pk: str, required
        """
        logger.info("Removing user from user group")
        payload = {"user_group": group_pk,
                   "users": user_pk}
        success, returned_data, status_code, error_msg = api_connection.exec_post_url(
            '/api/customers/usergroups/remove_user/', payload)
        if success:
            return "User successfully removed from user group", status_code
        return None

    @staticmethod
    def get_user_feature_access(api_connection, params={}):
        """Fetches accesses to features for user groups

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching user feature access")
        json_res = api_connection.exec_get_url('/api/customers/userfeatureaccesses/', params)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_user_feature_access_for_user_group(api_connection, group_pk):
        """Fetches features to user groups

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param group_pk: user group key
        :type group_pk: str, required
        """
        logger.info("Fetching user feature access")
        params = {'group': group_pk}
        json_res = api_connection.exec_get_url('/api/customers/userfeatureaccesses/', params)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def upsert_user_feature_access(api_connection, user_feature_access):
        """Upserts accesses to features for user groups

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Upserting user feature access")
        payload = user_feature_access.get_dict()
        key = int(payload['pk'])
        if key > 0:
            success, returned_data, status_code, error_msg = api_connection.exec_patch_url(
                '/api/customers/userfeatureaccesses/' + str(payload['pk']) + "/", payload)
        else:
            success, returned_data, status_code, error_msg = api_connection.exec_post_url(
                '/api/customers/userfeatureaccesses/', payload)
        if success:
            return returned_data
        return None

    @staticmethod
    def delete_user_feature_access(api_connection, pk):
        """Deletes features to user groups

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param pk: user feature access key
        :type pk: str, required
        """
        logger.info("Deleting user feature access")
        success, returned_data, status_code, error_msg = api_connection.exec_delete_url(
            '/api/customers/userfeatureaccesses/' + str(pk) + '/')
        if success:
            return "User feature access successfully deleted", status_code
        return None

    @staticmethod
    def get_user_url(api_connection, user_pk):
        """Fetches user from url

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param user_pk: personal key of user
        :type user_pk: str, required
        """
        return api_connection.get_base_url() + '/api/customers/profiles/' + str(user_pk) + "/"

    @staticmethod
    def send_password_reset_email(api_connection, email):
        """ Sends email to user with instructions for resetting password

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Sending password reset instructions to " + email)
        payload = {"email": email}
        success, returned_data, status_code, error_msg = api_connection.exec_post_url('/api/customers/password_reset/', payload)
        return success, returned_data, status_code, error_msg

    @staticmethod
    def reset_password(api_connection, payload):
        """ Resets password for users

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Resetting password")
        success, returned_data, status_code, error_msg = api_connection.exec_post_url('/api/customers/password_reset/confirm/',
                                                                                      payload)
        return success, returned_data, status_code, error_msg

    @staticmethod
    def validate_reset_token(api_connection, token):
        """ Checks if token for resetting password is valid

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Verifying reset token")
        payload = {"token": token}
        success, returned_data, status_code, error_msg = api_connection.exec_post_url('/api/customers/password_reset/validate_token/',
                                                                                      payload)
        return success, returned_data, status_code, error_msg
