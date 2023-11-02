"""
Wrapper for Token management
"""

import requests
from requests.auth import HTTPBasicAuth
import http.client
import logging
import environ
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
        self.token_type=None
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
        print("Validating", username, password)
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
        self.set_token(tok, "Token")
        print(self.get_authorization_header())
        print("We are OK for basic auth, return token", tok)
        return True, tok

    @staticmethod
    def get_internal_auth():
        env = environ.Env()
        auth_id = None if not 'ENERGYDESK_AUTH_ID' in env else env.str('ENERGYDESK_AUTH_ID')
        auth_secret = None if not 'ENERGYDESK_AUTH_SECRET' in env else env.str('ENERGYDESK_AUTH_SECRET')
        return auth_id, auth_secret
    #Example

    @staticmethod
    def __exec_impl_jwt_conversion(base_url, token, backend="google-oauth2"):
        auth_id, auth_secret=ApiConnection.get_internal_auth()
        http.client._MAXHEADERS = 1000
        server_url = base_url + "/auth/convert-token"
        payload = {
            "grant_type": "convert_token",
            "client_id": auth_id,
            "client_secret": auth_secret,
            "backend": backend,
            "token": token}
        print(payload)
        result = requests.post(server_url, json=payload)
        print(result)
        print(result.text)
        if result.status_code != 200:
            print("Could not validate user with backend")
            print(result.text)
            return None
        access_token = result.json()['access_token']
        return access_token

    @staticmethod
    def validate_jwt_token( base_url, token, backend="google-oauth2"):
        return ApiConnection.__exec_impl_jwt_conversion( base_url, token, backend)

    def validate_token(self, token, backend="google-oauth2"):
        access_token=ApiConnection.__exec_impl_jwt_conversion(self.get_base_url(), token, backend)
        self.set_token(access_token, "Bearer")
        return True

    def set_token(self, token, token_type="Bearer"):
        """Sets a token

        :param token: API token
        :type token: str, required
        :param token_type: bearer or token
        :type token_type: str, required
        """
        if token!="" and token_type=="Bearer":
            self.token_type=token_type
            self.token=token

        elif token!="" and token_type=="Token":
            self.token_type=token_type
            self.token=token

        else:
            logger.info("Token is Null")
            self.token_type=None
            self.token=token

    def get_current_token(self):
        return self.token

    def get_authorization_header(self):
        """Returns the authorization header
        """
        return {'Authorization':  str(self.token_type) + ' ' + str(self.token)}

    def exec_post_url_binary(self, trailing_url, payload, extra_headers={}):
        headers=self.get_authorization_header()
        for key in extra_headers:
            headers[key]=extra_headers[key]
        server_url= self.get_base_url() + trailing_url
        logger.info("Calling URL " + str(server_url))
        logger.debug("...with payload " + str(payload) + " and headers " + str(headers))
        return  requests.post(server_url, json=payload,   headers=headers)

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
        if result.status_code<210:
            if result.status_code>200 and result.text.strip()=="":
                return True, [], result.status_code, None
            json_data = result.json()
            return True, json_data, result.status_code, None
        else:
            logger.error("Problens calling EnergyDesk API " + str(result.status_code))
            if result.status_code==401:
                raise TokenException("Token is invalid")
            elif result.status_code==403:
                raise AuthorizationFailedException("Not authorized")
            return False, None, result.status_code, result.text

    def exec_delete_url(self, trailing_url,extra_headers={}):
        """Posts content from URL

        :param trailing_url: description...
        :type trailing_url: str, required
        :param extra_headers: description...
        :type extra_headers: str, required
        """
        headers = self.get_authorization_header()
        for key in extra_headers:
            headers[key] = extra_headers[key]
        server_url = self.get_base_url() + trailing_url
        logger.info("Calling URL " + str(server_url))
        result = requests.delete(server_url, headers=headers)
        if result.status_code < 210:
            if result.status_code > 200 and result.text.strip() == "":
                return True, [], result.status_code, None
            json_data = result.json()
            return True, json_data, result.status_code, None
        else:
            logger.error("Problens calling EnergyDesk API " + str(result.status_code))
            if result.status_code == 401:
                raise TokenException("Token is invalid")
            elif result.status_code==403:
                raise AuthorizationFailedException("Not authorized")
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
            elif result.status_code==403:
                raise AuthorizationFailedException("Not authorized")
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
        logger.debug("...with payload " + " and headers " + str(headers))
        if len(parameters.keys())>0:
            result = requests.get(server_url,  headers=headers, params=parameters)
            print(result.url)
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
            elif result.status_code==403:
                raise AuthorizationFailedException("Not authorized")
            return None


class Borg:
    _shared_state = {}
    def __init__(self):
        self.__dict__ = self._shared_state


class ApiCache(Borg):
    def __init__(self, api_conn=None):
        Borg.__init__(self)
        if api_conn is not None:
            self.api_conn=api_conn
