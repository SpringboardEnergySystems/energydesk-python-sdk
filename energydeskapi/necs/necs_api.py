import logging

logger = logging.getLogger(__name__)


class NecsApi:
    """Class for NECS API

    """

    @staticmethod
    def get_necs_certificates(api_connection):
        """Fetches NECS certificates

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching NECS certificates")
        json_res = api_connection.exec_get_url(
            '/api/necs/necs_certificates/')
        if json_res is not None:
            return json_res
        return None

    @staticmethod
    def get_necs_certificate_by_key(api_connection, pk):
        """Fetches NECS certificate from pk

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param pk: NECS certificate pk
        :type pk: str, required
        """
        logger.info("Fetching NECS certificate " + str(pk))
        json_res = api_connection.exec_get_url(
            '/api/necs/necs_certificates/' + str(pk) + '/')
        if json_res is not None:
            return json_res
        return None
