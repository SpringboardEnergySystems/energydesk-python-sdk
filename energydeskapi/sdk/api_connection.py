"""
Wrapper for Token management
"""
from typing import Optional, Any

import requests
from requests import Response
from requests.auth import HTTPBasicAuth
import http.client
import logging
import environ
logger = logging.getLogger(__name__)

class AuthorizationFailedException(Exception):
    pass


class TokenException(Exception):
    pass

class _api_connection:
    def __init__(self, base_url: str, bearer_token=None):
        self.base_url = base_url
        self.token_type=None
        if bearer_token is None:
            self.set_token("", "Token")
        else:
            self.set_token(bearer_token, "Bearer")

    def get_base_url(self) -> str:
        """Returns a string to be used as URL prefix for RET API
        """
        return self.base_url

    def set_base_url(self, base_url: str) -> None:
        self.base_url=base_url

    def get_token(self) -> str:
        return self.token

    def validate_via_basic_auth(self, username: str, password: str) -> tuple[bool, str]:
        # Making a get request
        #response = requests.get(self.get_base_url() + '/api/customers/profiles/',{"user__username": str(username)},
        #                        auth=HTTPBasicAuth(username, password))
        #print(response.json())
        logger.info(f"Validating with basic authentication {username}")
        response = requests.get(self.get_base_url() + '/api/energydesk/get-api-token/',{"user__username": str(username)},
                                auth=HTTPBasicAuth(username, password))
        if response is None:
            return False, "Unknown Error"
        if response.status_code > 210:
            logger.error(f"Logging in user {username} in appserver (api-get-token) got {response.status_code}. {'Wrong password' if response.status_code == 401 else ''}")
            return False, f"Problems logging in user {username}. {'Wrong password' if response.status_code == 401 else ''}"
        if 'token' not in response.json():
            if 'detail' in response.json():
                errmsg=response.json()['detail']
            else:
                errmsg=response.text
            logger.error(f"Failed login attempt with basic authentication {username}: {errmsg}")
            return False, errmsg
        tok=response.json()['token']
        self.set_token(tok, "Token")
        logger.debug(f"Header: {self.get_authorization_header()}")
        logger.info(f"We are OK for basic auth, return token {tok}")
        return True, tok

    @staticmethod
    def get_internal_auth() -> tuple[Optional[str], Optional[str]]:
        env = environ.Env()
        auth_id = None if not 'ENERGYDESK_AUTH_ID' in env else env.str('ENERGYDESK_AUTH_ID')
        auth_secret = None if not 'ENERGYDESK_AUTH_SECRET' in env else env.str('ENERGYDESK_AUTH_SECRET')
        return auth_id, auth_secret
    #Example

    @staticmethod
    def __exec_impl_jwt_conversion(base_url: str, token: str, backend: str="google-oauth2") -> Optional[str]:
        auth_id, auth_secret=ApiConnection.get_internal_auth()
        http.client._MAXHEADERS = 1000
        server_url = base_url + "/auth/convert-token"
        payload = {
            "grant_type": "convert_token",
            "client_id": auth_id,
            "client_secret": auth_secret,
            "backend": backend,
            "token": token}
        logger.debug(f"Jwt payload: {payload}")
        result = requests.post(server_url, json=payload)
        logger.debug(f"Result for {server_url} : {result} with text {result.text}")
        if result.status_code != 200:
            logger.error(f"Could not validate user with backend: {result.text}")
            return None
        access_token = result.json()['access_token']
        return access_token

    @staticmethod
    def validate_jwt_token( base_url: str, token: str, backend: str="google-oauth2") -> Optional[str]:
        return _api_connection.__exec_impl_jwt_conversion( base_url, token, backend)

    def validate_token(self, token: str, backend: str="google-oauth2") -> bool:
        access_token=_api_connection.__exec_impl_jwt_conversion(self.get_base_url(), token, backend)
        self.set_token(access_token, "Bearer")
        return True

    def set_token(self, token: str, token_type: str="Bearer") -> None:
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
            self.token_type=None
            self.token=token

    def get_current_token(self) -> str:
        return self.token

    def get_authorization_header(self) -> dict[str, Any]:
        """Returns the authorization header
        """
        if self.token is None or self.token=="":
            logger.debug("[api_connection] No token available, returning empty auth header")
            return {}
        auth_value = str(self.token_type) + ' ' + str(self.token)
        logger.debug(f"[api_connection] Authorization header: {self.token_type} {self.token[:10]}... (total length: {len(self.token)})")
        return {'Authorization': auth_value}

    def exec_post_url_binary(self, trailing_url: str, payload: dict, extra_headers: dict={}) -> Response:
        headers=self.get_authorization_header()
        for key in extra_headers:
            headers[key]=extra_headers[key]
        server_url= self._add_trailing_slash_if_missing(self.get_base_url() + trailing_url)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Calling POST URL binary {server_url} with payload {payload} and headers {headers}")
        return  requests.post(server_url, json=payload,   headers=headers)

    def exec_post_url(self, trailing_url: str, payload: dict, extra_headers: dict={}) -> tuple[bool, Optional[list|str], int, Optional[str]]:
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
        server_url= self._add_trailing_slash_if_missing(self.get_base_url() + trailing_url)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Calling POST URL {server_url} with payload {payload} and headers {headers}")
        result = requests.post(server_url, json=payload,   headers=headers)
        if result.status_code<210:
            if result.status_code>200 and result.text.strip()=="":
                return True, [], result.status_code, None
            if result.headers.get('content-type') != 'application/json':# Text data , e.g. CSV
                return  True, result.text, result.status_code, None
            json_data = result.json()
            return True, json_data, result.status_code, None
        else:
            logger.error(f"Problems calling post EnergyDesk API {server_url}: {result.status_code} {result.text}")
            if result.status_code==401:
                raise TokenException("Token is invalid")
            elif result.status_code==403:
                raise AuthorizationFailedException("Not authorized: {}".format(result.text))
            return False, None, result.status_code, result.text

    def exec_delete_url(self, trailing_url: str,extra_headers: dict={}) -> tuple[bool, Optional[list|str], int, Optional[str]]:
        """Posts content from URL

        :param trailing_url: description...
        :type trailing_url: str, required
        :param extra_headers: description...
        :type extra_headers: str, required
        """
        headers = self.get_authorization_header()
        for key in extra_headers:
            headers[key] = extra_headers[key]
        server_url = self._add_trailing_slash_if_missing(self.get_base_url() + trailing_url)
        logger.debug(f"Calling DELETE URL {server_url}")
        result = requests.delete(server_url, headers=headers)
        if result.status_code < 210:
            if result.status_code > 200 and result.text.strip() == "":
                return True, [], result.status_code, None
            json_data = result.json()
            return True, json_data, result.status_code, None
        else:
            logger.error(f"Problems calling delete EnergyDesk API {server_url}: {result.status_code} {result.text}")
            if result.status_code == 401:
                raise TokenException("Token is invalid")
            elif result.status_code==403:
                raise AuthorizationFailedException("Not authorized: {}".format(result.text))
            return False, None, result.status_code, result.text


    def exec_patch_url(self, trailing_url: str, payload: dict, extra_headers: dict={})-> tuple[bool, Optional[list|str], int, Optional[str]]:
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
        server_url= self._add_trailing_slash_if_missing(self.get_base_url() + trailing_url)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Calling PATCH URL {server_url} with payload {payload} and headers {headers}")
        result = requests.patch(server_url, json=payload,   headers=headers)
        if result.status_code<202:
            json_data = result.json()
            return True, json_data, result.status_code, None
        else:
            logger.error(f"Problems calling patch EnergyDesk API {server_url} {result} ")
            if result.status_code==401:
                raise TokenException("Token is invalid")
            elif result.status_code==403:
                raise AuthorizationFailedException("Not authorized: {}".format(result.text))
            return False, None, result.status_code, result.text


    def _add_trailing_slash_if_missing(self, server_url: str) -> str:
        return server_url if server_url.endswith("/") else server_url + "/"


    def exec_get_url(self, trailing_url: str,  parameters: dict={}, extra_headers: dict={}) -> dict | str | None:
        """Returns content from URL

        :param trailing_url: description...
        :type trailing_url: str, required
        :param extra_headers: description...
        :type extra_headers: str, required
        """

        headers=self.get_authorization_header()
        for key in extra_headers:
            headers[key]=extra_headers[key]
        server_url: str = self._add_trailing_slash_if_missing(self.get_base_url() + trailing_url)
        logger.info(f"Calling GET URL {server_url}")
        logger.info(f"[exec_get_url] Headers: Authorization={headers.get('Authorization', 'MISSING')[:30]}...")
        logger.debug(f"...with headers {headers.keys()}")
        if len(parameters.keys())>0:
            req = requests.Request('GET', server_url, headers=headers, params=parameters)
            prepared = req.prepare()
            print(prepared.url)
            result = requests.get(server_url,  headers=headers, params=parameters)
        else:
            result = requests.get(server_url, headers=headers)
        
        logger.info(f"[exec_get_url] Response status: {result.status_code}")

        if result.status_code<202:
            try:
                if result.headers.get('content-type')=="text/csv":
                    logger.info("It is CSV")
                    return result.text
                if result.headers.get('content-type') == "application/json":
                    return result.json()
                return result.text
            except:
                return None
        else:
            logger.error(f"Problems calling get EnergyDesk API {server_url} {result} ")
            if result.status_code==401:
                logger.error(f"[exec_get_url] 401 Unauthorized response body: {result.text[:500]}")
                raise TokenException("Token is invalid")
            elif result.status_code==403:
                raise AuthorizationFailedException("Not authorized: {}".format(result.text))
            return None


class ApiConnection(object):
    """This is a class for holding tokens used during login to Energy Desk REST API

      :param base_url: the prefix of the URL (examples: https://api-test.energydesk.no, http://127.0.0.1:(0000)
      :type base_url: str:
      """
    def __init__(self, base_url: str, bearer_token: Optional[str]=None):
        self.api_connection=_api_connection(base_url, bearer_token)
    def get_authorization_header(self) -> dict[str, Any]:
        return self.api_connection.get_authorization_header()
    def get_base_url(self) -> str:
        return self.api_connection.get_base_url()
    def set_base_url(self, base_url: str) -> None:
        self.api_connection.set_base_url(base_url)
    def validate_via_basic_auth(self, username: str, password: str) -> tuple[bool, str]:
        return self.api_connection.validate_via_basic_auth(username, password)
    def validate_token(self, token: str, backend: str="google-oauth2") -> bool:
        return self.api_connection.validate_token(token, backend)
    def set_token(self, token: str, token_type: str="Bearer") -> None:
        return self.api_connection.set_token(token, token_type)
    def get_token(self) -> str:
        return self.api_connection.get_token()
    def add_trailing_slash_if_missing(self, server_url: str) -> str:
        return self.api_connection._add_trailing_slash_if_missing(server_url)

    @staticmethod
    def validate_jwt_token( base_url: str, token: str, backend: str="google-oauth2") -> Optional[str]:
        return _api_connection.validate_jwt_token( base_url, token, backend)

    def exec_get_url(self, trailing_url: str, parameters: dict={}, extra_headers: dict={}) -> dict | list | str | None:
        return self.api_connection.exec_get_url(trailing_url, parameters, extra_headers)
    def exec_post_url(self, trailing_url: str, payload: dict, extra_headers: dict={}) -> tuple[bool, Optional[list|str], int, Optional[str]]:
        return self.api_connection.exec_post_url(trailing_url, payload, extra_headers)
    def exec_post_url_binary(self, trailing_url: str, payload: dict, extra_headers={}) -> Response:
        return self.api_connection.exec_post_url_binary(trailing_url, payload, extra_headers)
    def exec_patch_url(self, trailing_url: str, payload: dict, extra_headers={}) -> tuple[bool, Optional[list|str], int, Optional[str]]:
        return self.api_connection.exec_patch_url(trailing_url, payload, extra_headers)
    def exec_delete_url(self, trailing_url: str,extra_headers: dict={}) -> tuple[bool, Optional[list|str], int, Optional[str]]:
        return self.api_connection.exec_delete_url(trailing_url, extra_headers)


class ApiTempConnection:
    """ A variant of ApiConnection that is not singleton and can be created without affecting the tokens etc in the singleton
    SOmetimes we
      """

    def __init__(self, base_url: str, bearer_token: Optional[str]=None):
        self.api_connection = _api_connection(base_url, bearer_token)

    def get_authorization_header(self) -> dict[str, Any]:
        return self.api_connection.get_authorization_header()
    def get_base_url(self) -> str:
        return self.api_connection.get_base_url()
    def validate_via_basic_auth(self, username: str, password: str) -> tuple[bool, str]:
        return self.api_connection.validate_via_basic_auth(username, password)
    def validate_token(self, token: str, backend: str="google-oauth2") -> bool:
        return self.api_connection.validate_token(token, backend)
    def set_token(self, token: str, token_type: str="Bearer") -> None:
        return self.api_connection.set_token(token, token_type)
    def get_token(self) -> str:
        return self.api_connection.get_token()
    def set_base_url(self, base_url: str) -> None:
        self.api_connection.set_base_url(base_url)

    @staticmethod
    def validate_jwt_token(base_url: str, token: str, backend="google-oauth2") -> Optional[str]:
        return _api_connection.validate_jwt_token(base_url, token, backend)
    def exec_get_url(self, trailing_url: str, parameters: dict={}, extra_headers: dict={}) -> dict | str | None:
        return self.api_connection.exec_get_url(trailing_url, parameters, extra_headers)
    def exec_post_url(self, trailing_url: str, payload: dict, extra_headers: dict={}) -> tuple[bool, Optional[list|str], int, Optional[str]]:
        return self.api_connection.exec_post_url(trailing_url, payload, extra_headers)
    def exec_post_url_binary(self, trailing_url: str, payload: dict, extra_headers={}) -> Response:
        return self.api_connection.exec_post_url_binary(trailing_url, payload, extra_headers)

    def exec_patch_url(self, trailing_url: str, payload: dict, extra_headers: dict={}) -> tuple[bool, Optional[list|str], int, Optional[str]]:
        return self.api_connection.exec_patch_url(trailing_url, payload, extra_headers)

    def exec_delete_url(self, trailing_url: str, extra_headers: dict={}) -> tuple[bool, Optional[list|str], int, Optional[str]]:
        return self.api_connection.exec_delete_url(trailing_url, extra_headers)

class Borg:
    _shared_state = {}
    def __init__(self):
        self.__dict__ = self._shared_state


class ApiCache(Borg):
    def __init__(self, api_conn=None):
        Borg.__init__(self)
        if api_conn is not None:
            self.api_conn=api_conn

