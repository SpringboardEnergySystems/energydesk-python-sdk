import json
import logging

from energydeskapi.customers.users_api import UserGroup, UsersApi
from energydeskapi.sdk.common_utils import init_api


def register_user_group(api_conn, description):
    ast = UserGroup()
    ast.pk = 0
    ast.description = description
    success, returned_data, status_code, error_msg = UsersApi.upsert_user_groups(api_conn, ast)
    print(success, returned_data, status_code, error_msg)

def initialize_default_usergroups(api_conn):
    register_user_group("Administrators")