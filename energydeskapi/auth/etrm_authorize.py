import environ
import json
import logging
import pandas as pd
import pendulum
import pytz
import requests

from energydeskapi.customers.users_api import UsersApi
from energydeskapi.sdk.api_connection import ApiConnection
from energydeskapi.sdk.common_utils import init_api


def authorize_user_etrm(token):
    """
    Validate token and get user information from Django OAuth backend.

    Args:
        token: The OAuth access token to val
    """
    env = environ.Env()
    api_base_url = env.str('ENERGYDESK_URL')
    api_conn = ApiConnection(api_base_url)
    api_conn.set_token(token, "Bearer")
    usrprofile = UsersApi.get_user_profile(api_conn)
    if usrprofile is not None:
        return (usrprofile['role_pk'],usrprofile['role'])
    else:
        print("No user profile found. Please check the API endpoint: ")
    return (None,None)