import logging
import pandas as pd
logger = logging.getLogger(__name__)


class AuditLogApi:
    """ Class for audit log REST API
    """

    @staticmethod
    def get_audit_log(api_connection, parameters={}):
        """Fetches all assets

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/audit/auditlog/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_audit_log_embedded(api_connection, parameters={}):
        """Fetches audit log with embedded structure for user and contracts

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/audit/auditlog/embedded/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_audit_log_object(api_connection, pk):
        """Fetches audit log with embedded structure for user and contracts

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        parameters = {'audit_object_id':pk}
        json_res = api_connection.exec_get_url('/api/audit/auditlog/embedded/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_audit_log_by_key(api_connection, pk):
        """Fetches audit log with embedded structure for user and contracts

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param pk:  key of audit object
        :type pk: str, required
        """
        logger.info("Fetching audit log object with key " + str(pk))
        json_res=api_connection.exec_get_url('/api/audit/auditlog/' + str(pk) + "/")
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_audit_log_types(api_connection, parameters={}):
        """Fetches all audit log types

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/audit/auditlogtypes/', parameters)
        if json_res is None:
            return None
        return json_res
