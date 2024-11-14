import logging
logger = logging.getLogger(__name__)


class DwhApi:
    """Class for user access to Datawarehouse
    """
    @staticmethod
    def get_contract_dimension(api_connection, parameters={}):
        """Fetches  contracts
        """
        json_res = api_connection.exec_get_url('/api/dwh/contracts/', parameters)
        if json_res is None:
            return None
        return json_res
    @staticmethod
    def get_report_dimension(api_connection, parameters={}):
        """Fetches  reports
        """
        json_res = api_connection.exec_get_url('/api/dwh/reports/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_timestamp_dimension(api_connection, parameters={}):
        """Fetches  reports
        """
        json_res = api_connection.exec_get_url('/api/dwh/times/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_contract_timeseries(api_connection, parameters={}):
        """Fetches  reports
        """
        json_res = api_connection.exec_get_url('/api/dwh/contracttimeseries/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_periodview_timeseries(api_connection, parameters={}):
        """Fetches  reports
        """
        json_res = api_connection.exec_get_url('/api/dwh/periodviewtimeseries/latest/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_report_types(api_connection, parameters={}):
        """Fetches  reports
        """
        json_res = api_connection.exec_get_url('/api/dwh/reporttypes/', parameters)
        if json_res is None:
            return None
        return json_res