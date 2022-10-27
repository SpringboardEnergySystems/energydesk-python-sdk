"""
Wrapper for Token management
"""

import requests
from requests.auth import HTTPBasicAuth
import http.client
import json
import logging
logger = logging.getLogger(__name__)

class AuthorizationFailedException(Exception):
    pass


class TokenException(Exception):
    pass

class ApiConnection(object):
    """This is a class for holding tokens used during login to Energy Desk REST API

      :param base_url: the prefix of the URL (examples: https://api-test.energydesk.no, http://127.0.0.1:(0000)
      :type base_url: str:

      """

    def __init__(self, base_url, bearer_token=None):
        self.base_url = base_url
        if bearer_token is None:
            self.set_token("", "Token")
        else:
            self.set_token(bearer_token, "Bearer")

    def get_base_url(self):
        """Returns a string to be used as URL prefix for RET API
        """
        return self.base_url


    def validate_via_basic_auth(self, username, password):
        # Making a get request
        #response = requests.get(self.get_base_url() + '/api/customers/profiles/',{"user__username": str(username)},
        #                        auth=HTTPBasicAuth(username, password))
        #print(response.json())
        response = requests.get(self.get_base_url() + '/api/energydesk/get-api-token/',{"user__username": str(username)},
                                auth=HTTPBasicAuth(username, password))
        if response is None:
            return False, "Unknown Error"
        if 'token' not in response.json():
            if 'detail' in response.json():
                errmsg=response.json()['detail']
            else:
                errmsg=response.text
            logger.error("Failed login attempt " + str(username) + " " + errmsg)
            return False, errmsg
        tok=response.json()['token']
        print(response.json()['token'])
        self.set_token(tok, "Token")
        return True, "Login OK"

    def validate_token(self, token):
        """Validates a token

        :param token: API token
        :type token: str, required
        """
        print("Validation....", self.base_url)
        http.client._MAXHEADERS = 1000
        server_url = self.get_base_url() + "/auth/convert-token"
        payload = {
            "grant_type": "convert_token",
            "client_id": "client_id",
            "client_secret": "client_secret",
            "backend": "google-oauth2",
            "token": token}
        result = requests.post(server_url, json=payload)
        if result.status_code != 200:
            print("Could not validate user with backend")
            return False
        access_token = result.json()['access_token']
        self.set_token(access_token, "Bearer")
        return True

    def set_token(self, token, token_type="Bearer"):
        """Sets a token

        :param token: API token
        :type token: str, required
        :param token_type: bearer or token
        :type token_type: str, required
        """
        if self.token is not None and self.token!="" and self.token_type=="Token":
            print("Token already set from Django")
        else:
            self.token_type=token_type
            self.token=token
            print("Setting token in object",self.token_type, self.token )

    def get_current_token(self):
        return self.token

    def get_authorization_header(self):
        """Returns the authorization header
        """
        return {'Authorization':  self.token_type + ' ' + self.token}

    def exec_post_url(self, trailing_url, payload, extra_headers={}):
        """Posts content from URL

        :param trailing_url: description...
        :type trailing_url: str, required
        :param payload: description...
        :type payload: str, required
        :param extra_headers: description...
        :type extra_headers: str, required
        """
        headers=self.get_authorization_header()
        for key in extra_headers:
            headers[key]=extra_headers[key]
        server_url= self.get_base_url() + trailing_url
        logger.info("Calling URL " + str(server_url))
        logger.debug("...with payload " + str(payload) + " and headers " + str(headers))
        result = requests.post(server_url, json=payload,   headers=headers)
        if result.status_code<202:
            json_data = result.json()
            return True, json_data, result.status_code, None
        else:
            logger.error("Problens calling EnergyDesk API " + str(result.status_code))
            if result.status_code==401:
                raise TokenException("Token is invalid")
            return False, None, result.status_code, result.text

    def exec_patch_url(self, trailing_url, payload, extra_headers={}):
        """Posts content from URL

        :param trailing_url: description...
        :type trailing_url: str, required
        :param payload: description...
        :type payload: str, required
        :param extra_headers: description...
        :type extra_headers: str, required
        """
        headers=self.get_authorization_header()
        for key in extra_headers:
            headers[key]=extra_headers[key]
        server_url= self.get_base_url() + trailing_url
        logger.info("Calling URL " + str(server_url))
        logger.debug("...with payload " + str(payload) + " and headers " + str(headers))
        result = requests.patch(server_url, json=payload,   headers=headers)
        if result.status_code<202:
            json_data = result.json()
            return True, json_data, result.status_code, None
        else:
            logger.error("Problens calling EnergyDesk API- (patch) " + str(result) + " " )
            if result.status_code==401:
                raise TokenException("Token is invalid")
            return False, None, result.status_code, result.text

    def exec_get_url(self, trailing_url,  parameters={}, extra_headers={}):
        """Returns content from URL

        :param trailing_url: description...
        :type trailing_url: str, required
        :param extra_headers: description...
        :type extra_headers: str, required
        """
        headers=self.get_authorization_header()
        for key in extra_headers:
            headers[key]=extra_headers[key]
        server_url= self.get_base_url() + trailing_url
        logger.info("Calling URL " + str(server_url))
        logger.info("...with payload " + " and headers " + str(headers))
        if len(parameters.keys())>0:
            result = requests.get(server_url,  headers=headers, params=parameters)
        else:
            result = requests.get(server_url, headers=headers)
        if result.status_code<202:
            try:
                json_data = result.json()
            except:
                return None
            return json_data
        else:
            logger.error("Problens calling EnergyDesk API " + str(result) )
            if result.status_code==401:
                raise TokenException("Token is invalid")
            return None