import logging

logger = logging.getLogger(__name__)


class NecsApi:
    """Class for NECS API

    """

    @staticmethod
    def get_necs_certificates(api_connection, parameters={}):
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

    @staticmethod
    def get_necs_transactions(api_connection, parameters={}):
        """Fetches NECS transactions

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching NECS transactions")
        json_res = api_connection.exec_get_url(
            '/api/necs/necs_transactions/')
        if json_res is not None:
            return json_res
        return None

    @staticmethod
    def get_necs_transaction_by_key(api_connection, pk):
        """Fetches NECS transaction from pk

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param pk: NECS transaction pk
        :type pk: str, required
        """
        logger.info("Fetching NECS transaction " + str(pk))
        json_res = api_connection.exec_get_url(
            '/api/necs/necs_transactions/' + str(pk) + '/')
        if json_res is not None:
            return json_res
        return None

    @staticmethod
    def get_necs_transaction_bundles(api_connection, parameters={}):
        """Fetches NECS transaction bundles

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching NECS transaction bundles")
        json_res = api_connection.exec_get_url(
            '/api/necs/necs_transaction_bundles/')
        if json_res is not None:
            return json_res
        return None

    @staticmethod
    def get_necs_transaction_bundle_by_key(api_connection, pk):
        """Fetches NECS transaction bundle from pk

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param pk: NECS transaction bundle pk
        :type pk: str, required
        """
        logger.info("Fetching NECS transaction bundle " + str(pk))
        json_res = api_connection.exec_get_url(
            '/api/necs/necs_transaction_bundles/' + str(pk) + '/')
        if json_res is not None:
            return json_res
        return None
